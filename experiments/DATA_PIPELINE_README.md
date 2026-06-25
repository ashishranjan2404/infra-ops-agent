# SRE-Degrees — Data Pipeline README

This document explains every data source, every pipeline, the prompts used to
generate data, and the Python files that drive each step. Built for the team
(Ashish, Wenji, Sylvie) to continue the work.

---

## Architecture Diagram (text)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES (seeds)                             │
├──────────────────┬──────────────────┬──────────────────┬───────────────┤
│  19 Real         │  15 Spec Packs   │  danluu repo     │  FIREBALL     │
│  Postmortems     │  (templated      │  (700+ PMs)      │  D&D dataset  │
│  (hand-extracted)│  incident types) │  github.com/     │  HuggingFace  │
│                  │                  │  danluu/post-    │  CC-BY-4.0    │
│  catalog.md      │  specs/*.json    │  mortems         │               │
└────────┬─────────┴────────┬─────────┴────────┬─────────┴───────┬───────┘
         │                  │                  │                 │
         ▼                  ▼                  │                 │
┌──────────────────────────────────┐          │                 │
│  PIPELINE 1: SFT/DPO Generator   │          │                 │
│  opensre-traj/generate.py        │          │                 │
│  opensre-traj/generate_pathc.py  │          │                 │
│                                  │          │                 │
│  Input: 15 spec packs × seeds    │          │                 │
│  Output: 150K SFT + 30K DPO +    │          │                 │
│          20K rejections          │          │                 │
│  → HuggingFace: quantranger/     │          │                 │
│    infra-ops-incidents           │          │                 │
│  Purpose: OFFLINE training       │          │                 │
│  (SFT + DPO fine-tuning)         │          │                 │
└──────────────────────────────────┘          │                 │
                                              │                 │
         ┌────────────────────────────────────┘                 │
         ▼                                                      │
┌──────────────────────────────────────────┐                    │
│  PIPELINE 2: Interactive RLVR Corpus     │                    │
│  opensre-traj/generate.py (same file,    │                    │
│    different mode: --n 20)               │                    │
│  opensre-traj/hud_env.py (HUD env)       │                    │
│                                          │                    │
│  Input: 15 spec packs + 19 real PMs      │                    │
│  Output: 319-scenario corpus             │                    │
│          (out/trajectories.jsonl)        │                    │
│          - 83 synthetic (15 types × ~5)  │                    │
│          - 114 real (19 PMs × ~6 vars)   │                    │
│          - 122 additional variants       │                    │
│  → HuggingFace: opensre-traj HUD env     │                    │
│  Purpose: ONLINE RLVR/GRPO training      │                    │
│  (agent investigates via MCP tools,      │                    │
│   gets reward from deterministic judge)  │                    │
└──────────────────────────────────────────┘                    │
                                                                │
         ┌──────────────────────────────────────────────────────┘
         ▼                                                      ▼
┌──────────────────────────────────────────┐  ┌─────────────────────────┐
│  PIPELINE 3: Eval Benchmark (pass@k)     │  │  PIPELINE 4: Fireball   │
│  experiments/build_incidents.py          │  │  Transfer (E2)          │
│  rex/eval_pass_at_k.py                   │  │  experiments/ralph_outputs/
│  rex/harness.py (sim engine)             │  │    E2/artifacts/        │
│                                          │  │    fireball_fetch.py    │
│  Input: 19 real PMs + danluu repo +      │  │    fireball_convert.py  │
│         sim engine schema                │  │                         │
│  Output: 62 scenario YAMLs               │  │  Input: lara-martin/    │
│         (42 for eval: 8 simple,          │  │    FIREBALL (HuggingFace)│
│          14 cascade, 10 novel)           │  │  Output: converted      │
│  Purpose: pass@k evaluation              │  │    trajectories in      │
│  (the 90% vs 23% numbers)               │  │    SRE format           │
└──────────────────────────────────────────┘  └─────────────────────────┘
```

---

## Pipeline 1: SFT/DPO Training Data (offline)

### What it produces
150,000 SFT trajectories + 30,000 DPO preference pairs + 20,000 labeled rejections.

### Data source
15 templated incident spec packs at `opensre-traj/specs/*.json`:
```
oom_kill, cpu_saturation, disk_pressure, crashloop, latency_spike,
dns_failure, memory_leak, cert_expiry, cache_stampede, upstream_5xx,
bad_deploy_errors, db_pool_exhaustion, node_not_ready, consumer_lag,
stuck_rollout
```

Each spec pack is a JSON file with: incident type, alert template, placeholder
defaults (service names, pod names, node names), evidence templates per tool,
and the ground-truth root cause + correct fix.

### Generator files
- `opensre-traj/generate.py` — renders N variants per spec pack, outputs
  alert.json, scenario.yml, evidence files, answer.yml, and flattened
  trajectories.jsonl
- `opensre-traj/generate_pathc.py` — generates failure trajectories + DPO
  winner/loser preference pairs from the same specs
- `opensre-traj/lib_opensre.py` — shared library: subst_map, substitute,
  render_trajectory, TOOL_EVIDENCE

### How to run
```bash
cd opensre-traj
python3 generate.py --n 20          # 20 variants per incident type
python3 generate_pathc.py --rej 20000 --pairs 30000
```

### Where the data lives
HuggingFace: `quantranger/infra-ops-incidents`
- incidents.jsonl (150K, 434 MB)
- pairs.jsonl (30K, 177 MB)
- rejections.jsonl (20K, 60 MB)

### NOT used for evaluation
This data is for offline SFT/DPO fine-tuning only. The 42-incident eval
benchmark is completely separate (Pipeline 3).

---

## Pipeline 2: Interactive RLVR/GRPO Corpus (online)

### What it produces
319-scenario interactive environment where an agent investigates incidents
via 8 diagnostic MCP tools and gets graded.

### Data sources
1. The same 15 spec packs (83 synthetic scenarios)
2. The 19 real postmortems from catalog.md (114 real scenarios, each with
   source_company + source_url back to the first-party postmortem)
3. Additional variants generated by parameterizing the above (122 more)

### Generator + environment files
- `opensre-traj/generate.py` (same file, `--n 20` mode) — generates the
  319-scenario corpus at `opensre-traj/out/trajectories.jsonl`
- `opensre-traj/hud_env.py` — HUD v6 environment: wraps the 319-scenario
  corpus into an interactive investigation env with 8 MCP tools
  (describe_pod, get_events, get_logs, get_metrics, query_traces, etc.)
- `opensre-traj/hud_env_static.py` — no-tools variant for models without
  function-calling
- `opensre-traj/train_rft.py` — GRPO/RFT training driver via HUD Tinker
- `opensre-traj/train_rft_v2.py` — v2 with deterministic judge + 10 tasks

### The prompt (what the agent sees)
```
You are an SRE investigating an incident. Use the diagnostic tools to
gather evidence, then state your root cause, category, and fix.

Alert: [alert from scenario]
Available tools: describe_pod, get_events, get_logs, get_metrics,
  query_traces, get_deployment_status, check_connectivity, get_resource_usage

State your diagnosis as:
ROOT_CAUSE: <1-2 sentences: the specific failing component and the mechanism>
CATEGORY: <one of: oom, cpu, disk, network, config, cert, cache, db, deploy>
FIX: <the remediation tool + target>
```

### The reward function (deterministic, P0 fix)
File: `rex/scoring.py`
```
r = 0.30 * I[diagnosis_correct] + 0.25 * cfix + 0.45 * I[resolved] - 0.60 * I[trap]
```
- diagnosis_correct: deterministic keyword-set judge (no LLM, no network)
- cfix: graded (1.0 correct tool+target, 0.5 correct tool wrong target, 0 neither)
- resolved: did the sim engine's SLO metric recover?
- trap: did the agent take a trap action (naive fix that worsens it)?

### How to run
```bash
cd opensre-traj
set -a; source ~/.zshrc; set +a   # export HUD_API_KEY

# Fork a trainable model
../.venv-hud/bin/hud models fork Qwen/Qwen3-8B --name opensre-qwen3-8b

# Smoke test
../.venv-hud/bin/python train_rft_v2.py --model <slug> --tasks 0,1 --group 4 --steps 1 --smoke

# Real run
../.venv-hud/bin/python train_rft_v2.py --model <slug> --tasks 0,1,2,3,4,5,6,7,8,9 \
  --group 6 --steps 50 --out runs/train_qwen3-8b_v2.jsonl
```

### Where the data lives
- `opensre-traj/out/trajectories.jsonl` (319 scenarios)
- `opensre-traj/out/hud_traces/` (197 graded trajectories across model spanning set)
- HuggingFace: the HUD trajectories dataset (197 trajectories, see
  `opensre-traj/out/HF_README.md`)

---

## Pipeline 3: Evaluation Benchmark (pass@k)

### What it produces
42-incident benchmark with pass@1/2/5, Wilson CIs, McNemar's test.

### Data sources
1. 19 real postmortems (`opensre-traj/real-incidents/catalog.md`)
2. danluu/post-mortems repo (https://github.com/danluu/post-mortems) — 700+
   categorized postmortem links, used to source novel incidents
3. The sim engine schema (`sim/spec.py`, `sim/engine.py`)

### Generator + eval files
- `experiments/build_incidents.py` — reads the 19-postmortem catalog + sim
  schema + danluu repo, generates YAML scenario specs
- `rex/eval_pass_at_k.py` — runs each incident k times, records binary
  pass/fail, computes pass@k with Wilson CIs
- `rex/harness.py` — the sim engine: load_scenario, run_plan, is_safe
- `rex/scoring.py` — the reward function (deterministic judge)
- `experiments/compute_pass_at_k.py` — pass@k calculator (unbiased estimator)

### Scenario spec format (YAML)
```yaml
meta:
  id: 50-circleci-kubeproxy-iptables
  title: CircleCI kube-proxy/iptables version skew
  source: real
  urls: [https://discuss.circleci.com/...]
topology:
  nodes: [kube-proxy, core-dns, rabbitmq, ...]
  edges: [[kube-proxy, core-dns], ...]
root_cause:
  location: kube-proxy
  kind: version_skew
  hidden: true
slo:
  - metric: svc_latency
    direction: lt
    threshold: 500
trap_actions:
  - tool: restart_service
    target: core-dns
    reason: "breaks DNS fully"
canonical_fix:
  steps:
    - tool: restart_service
      target: kube-proxy
assertions:
  cascades: true
  loudest_alert_not_cause: true
  fix_resolves: true
```

### How to run
```bash
cd /Users/mei/rl
set -a; source ~/.zshrc; set +a

# Full 42-incident pass@k evaluation
python3 -m rex.eval_pass_at_k --model glm-5p2 --per-family 5 --seeds 3 \
  --conditions zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle

# Just compute pass@k from existing data
python3 experiments/compute_pass_at_k.py
```

### Where the data lives
- `scenarios/cidg/*.yaml` (10 original)
- `scenarios/cidg/generated/*.yaml` (52 generated)
- `rex/runs/ablation.json` (original 5-incident ablation)
- `rex/runs/frontier.json` (5-model frontier sweep)
- `rex/runs/harness_synth_v2.json` (harness synthesis results)
- `experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json` (42-incident pass@k)
- `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` (750-episode ablation)

---

## Pipeline 4: FIREBALL Cross-Domain Transfer

### What it produces
Converted D&D game trajectories in SRE format, for testing cross-domain
transfer learning (Claim 2).

### Data source
FIREBALL dataset: Zhu et al., ACL 2023, arXiv:2305.01528
HuggingFace: `lara-martin/FIREBALL` (CC-BY-4.0, 1471 JSONL shards, 100K-1M rows)

### Files
- `experiments/ralph_outputs/E2/artifacts/fireball_fetch.py` — downloads
  shards from HuggingFace
- `experiments/ralph_outputs/E2/artifacts/fireball_schema.py` — schema
  validation (17-key format)
- `experiments/ralph_outputs/E2/artifacts/fireball_convert.py` — converts
  FIREBALL turns to SRE trajectory format
- `experiments/ralph_outputs/E2/artifacts/test_fireball_convert.py` — 7
  pytest cases

### Mapping (D&D → SRE)
```
observation      ← before_utterances + combat_state_before
actions          ← commands_norm
tools_used       ← command verbs
result           ← automation_results
target           ← after_utterances
next_observation ← combat_state_after
```

### How to run
```bash
cd experiments/ralph_outputs/E2/artifacts
python3 fireball_fetch.py --shards 5    # download 5 shards
python3 fireball_convert.py --input <shard.jsonl> --output fireball_sre.jsonl
```

---

## External Data Sources Summary

| Source | What it is | Where it's used | URL |
|--------|-----------|-----------------|-----|
| 19 real postmortems | Hand-extracted from company blogs | Pipeline 2 (RLVR), Pipeline 3 (eval) | See catalog.md for per-incident URLs |
| danluu/post-mortems | 700+ postmortem links, categorized | Pipeline 3 (novel incidents) | https://github.com/danluu/post-mortems |
| SREGym | 90-problem benchmark | Competitive comparison only | https://github.com/SREGym/SREGym |
| FIREBALL D&D | Game trajectory dataset | Pipeline 4 (transfer) | https://huggingface.co/datasets/lara-martin/FIREBALL |
| HuggingFace (ours) | 200K SFT/DPO trajectories | Pipeline 1 (training) | https://huggingface.co/datasets/quantranger/infra-ops-incidents |
| HuggingFace (ours) | 197 HUD trajectories | Pipeline 2 (RLVR spanning set) | See opensre-traj/out/HF_README.md |

---

## Infrastructure Notes (for Wenji)

### Current backend: HUD (hud.ai)
- Inference gateway: routes to Fireworks (glm-5p2, minimax-m3), OpenAI
  (gpt-5.5), Anthropic (claude), Google (gemini), DeepSeek
- Training backend: HUD Tinker (GPU, GRPO/GRPO)
- API key: `HUD_API_KEY` in ~/.zshrc (export with `set -a; source ~/.zshrc; set +a`)

### Suggested: Daytona + Modal (for efficiency)
Per the discussion, the team can improve efficiency by:
1. **Modal** (modal.com) — serverless GPU for the 50-step RFT runs that are
   currently compute-blocked. H100 instances via Unsloth QLoRA. Much faster
   than HUD Tinker's 75-90s/step.
2. **Daytona** (daytona.io) — dev environments for reproducible eval. Spin up
   a container with vLLM + the repo, run pass@k locally without API latency.

### To switch to Modal for training:
```bash
# Replace the HUD Tinker backend with Modal
pip install modal
modal deploy opensre-traj/train_rft_modal.py  # (needs to be written)
# The train_rft_v2.py is structured to accept any backend that implements
# TrainingClient.step() — swap HUD Tinker for Modal.
```

### To set up local vLLM for eval (fixes the API latency issue):
```bash
# This would have prevented the ablation stalling overnight
pip install vllm
vllm serve Qwen/Qwen3-8B --port 8000
# Then point eval_pass_at_k.py at localhost:8000 instead of the HUD gateway
```

---

## Quick Reference: Which file does what

| File | Pipeline | What it does |
|------|----------|-------------|
| opensre-traj/specs/*.json | 1, 2 | 15 templated incident spec packs |
| opensre-traj/generate.py | 1, 2 | Generates SFT data + interactive corpus |
| opensre-traj/generate_pathc.py | 1 | Generates DPO pairs + rejections |
| opensre-traj/lib_opensre.py | 1, 2 | Shared: subst_map, substitute, render_trajectory |
| opensre-traj/hud_env.py | 2 | HUD v6 interactive environment (8 MCP tools) |
| opensre-traj/train_rft.py | 2 | GRPO/RFT training driver (HUD Tinker) |
| opensre-traj/train_rft_v2.py | 2 | v2: deterministic judge, 10 tasks, reset-head |
| opensre-traj/real-incidents/catalog.md | 2, 3 | 19 real postmortems (the seed) |
| experiments/build_incidents.py | 3 | Generates 42 YAML scenario specs |
| rex/eval_pass_at_k.py | 3 | Full pass@k evaluation pipeline |
| rex/harness.py | 3 | Sim engine: load_scenario, run_plan, is_safe |
| rex/scoring.py | 2, 3 | Reward function (deterministic judge) |
| experiments/compute_pass_at_k.py | 3 | pass@k calculator (unbiased estimator) |
| experiments/ralph_outputs/E2/artifacts/fireball_*.py | 4 | FIREBALL fetch + convert |
| tools_registry.json | 1, 2 | 25 tools with trust tiers |
| verify.py | 3 | Verifiable reward — SLO check |
