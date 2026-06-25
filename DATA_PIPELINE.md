# SRE-Degrees — Data Pipeline & Source Documentation

> **For Beibei and Wenji.** This file documents every data source, every
> pipeline, the exact prompts used to generate data, and the Python files
> that drive each step. Follow this to reproduce or extend any pipeline.

---

## Architecture Diagram

Open `experiments/data_pipeline_architecture.html` in any browser for an
interactive dark-themed SVG diagram showing all 4 pipelines and data flows.

A static PNG version is at `experiments/data_pipeline_architecture.png`.

---

## Pipeline 1: SFT/DPO Training Data (offline, 200K trajectories)

### What it produces
150,000 SFT trajectories + 30,000 DPO preference pairs + 20,000 labeled
rejections. Used for offline fine-tuning (SFT + DPO). NOT used for evaluation.

### Data source
**15 templated incident spec packs** at `opensre-traj/specs/*.json`:
```
oom_kill.json, cpu_saturation.json, disk_pressure.json, crashloop.json,
latency_spike.json, dns_failure.json, memory_leak.json, cert_expiry.json,
cache_stampede.json, upstream_5xx.json, bad_deploy_errors.json,
db_pool_exhaustion.json, node_not_ready.json, consumer_lag.json,
stuck_rollout.json
```
Each spec pack is a JSON file with: incident type, alert template, placeholder
defaults (service names, pod names, node names), evidence templates per tool,
ground-truth root cause + correct fix.

**25-tool registry** at `tools_registry.json` (trust tiers: autonomous/approval/blocked).

**External source:** None. This data is fully synthetic/templated.

### Python files
| File | Role |
|------|------|
| `opensre-traj/generate.py` | Renders N variants per spec pack → SFT trajectories |
| `opensre-traj/generate_pathc.py` | Generates failure trajectories + DPO pairs |
| `opensre-traj/lib_opensre.py` | Shared: `render_trajectory()`, `TOOL_EVIDENCE`, `subst_map()` |

### Prompt template (the trajectory structure)
The `render_trajectory()` function in `lib_opensre.py` builds FIREBALL-style
alternating assistant/tool trajectories:

```
Step 1 (assistant): "Triage the alert by reading the highest-signal source first."
         action: {tool: "describe_pod", args: {service_id: "payments", namespace: "rlvr-target"}}
Step 2 (tool):     {success: true, notes: "returned k8s_pods.json", evidence_ref: "k8s_pods.json"}
Step 3 (assistant): "Corroborate with get_events before concluding."
         action: {tool: "get_events", args: {service_id: "payments", namespace: "rlvr-target"}}
Step 4 (tool):     {success: true, notes: "returned k8s_events.json", ...}
...
Step N (assistant): "Root cause identified. Applying remediation."
         action: {tool: "restart_pod", args: {target: "payments-7b6b9dfb7c-lv9ld"}}
Step N+1 (tool):    {success: true, metric_before: {memory: 128Mi}, metric_after: {memory: 256Mi}}
```

The 9 diagnostic tools available:
```
describe_pod, get_pods, get_events, get_logs, get_node_status,
get_deployment_status, get_metrics, get_alerts, query_traces
```

### How to run
```bash
cd opensre-traj
python3 generate.py --n 20          # 20 variants per incident type
python3 generate_pathc.py --rej 20000 --pairs 30000
```

### Where the data lives
HuggingFace: `quantranger/infra-ops-incidents`
- `incidents.jsonl` (150K, 434 MB) — SFT trajectories
- `pairs.jsonl` (30K, 177 MB) — DPO preference pairs
- `rejections.jsonl` (20K, 60 MB) — Labeled failures

---

## Pipeline 2: RLVR/GRPO Training (online, 319-scenario corpus)

### What it produces
Interactive environment where an agent investigates incidents via 8 MCP
diagnostic tools and gets graded by a deterministic reward function.

### Data sources
1. **15 spec packs** (same as Pipeline 1) → 83 synthetic scenarios
2. **19 real postmortems** (`opensre-traj/real-incidents/catalog.md`) → 114 real
   scenarios, each with `source_company` + `source_url` back to the first-party
   postmortem
3. **Parameterized variants** of the above → 122 additional scenarios

Total: 319 scenarios at `opensre-traj/out/trajectories.jsonl`

### Python files
| File | Role |
|------|------|
| `opensre-traj/generate.py` | Generates the 319-scenario corpus (same file, `--n 20` mode) |
| `opensre-traj/hud_env.py` | HUD v6 environment: wraps corpus into interactive investigation |
| `opensre-traj/hud_env_static.py` | No-tools variant (for models without function-calling) |
| `opensre-traj/train_rft.py` | GRPO/RFT training driver (HUD Tinker backend) |
| `opensre-traj/train_rft_v2.py` | v2: deterministic judge + 10 tasks + reset-head |
| `rex/scoring.py` | The reward function (deterministic judge, P0 fix) |

### Agent prompt (what the agent sees during training)
```
You are an SRE investigating an incident. Use the diagnostic tools to
gather evidence, then state your root cause, category, and fix.

ALERT:
{alert from scenario}

Available tools: describe_pod, get_events, get_logs, get_metrics,
  query_traces, get_deployment_status, check_connectivity, get_resource_usage

State your diagnosis as:
ROOT_CAUSE: <1-2 sentences: the specific failing component and the mechanism>
ROOT_CAUSE_CATEGORY: <one of: oom, cpu, disk, network, config, cert, cache, db, deploy>
FIX: <the single remediation action you would run>
```

### Reward function (deterministic, no LLM judge)
File: `rex/scoring.py`
```
r = 0.30 * I[diagnosis_correct] + 0.25 * cfix + 0.45 * I[resolved] - 0.60 * I[trap]
```
- `diagnosis_correct`: deterministic keyword-set judge (no LLM, no network)
- `cfix`: graded (1.0 = correct tool + target, 0.5 = correct tool wrong target, 0 = neither)
- `resolved`: did the sim engine's SLO metric recover?
- `trap`: did the agent take a trap action (naive fix that worsens it)?

### How to run
```bash
cd opensre-traj
set -a; source ~/.zshrc; set +a   # export HUD_API_KEY

# Fork a trainable model
../.venv-hud/bin/hud models fork Qwen/Qwen3-8B --name opensre-qwen3-8b

# Smoke test
../.venv-hud/bin/python train_rft_v2.py --model <slug> --tasks 0,1 --group 4 --steps 1 --smoke

# Real run (50 steps)
../.venv-hud/bin/python train_rft_v2.py --model <slug> --tasks 0,1,2,3,4,5,6,7,8,9 \
  --group 6 --steps 50 --out runs/train_qwen3-8b_v2.jsonl
```

### Where the data lives
- `opensre-traj/out/trajectories.jsonl` (319 scenarios)
- `opensre-traj/out/hud_traces/` (197 graded trajectories)
- HuggingFace: see `opensre-traj/out/HF_README.md`

---

## Pipeline 3: Evaluation Benchmark (pass@k, 42 incidents)

### What it produces
pass@1/2/5 with Wilson 95% CIs and McNemar's paired test. The 90% vs 23% numbers.

### Data sources
1. **19 real postmortems** (`opensre-traj/real-incidents/catalog.md`) — hand-extracted
   from first-party blog posts by CircleCI, Datadog, Slack, GitHub, Cloudflare, AWS,
   LaunchDarkly, incident.io
2. **danluu/post-mortems repo** — 700+ categorized postmortem links.
   URL: https://github.com/danluu/post-mortems
3. **Sim engine schema** (`sim/spec.py`, `sim/engine.py`)

### Python files
| File | Role |
|------|------|
| `experiments/build_incidents.py` | Reads 19 PMs + danluu + sim schema → generates YAML specs |
| `rex/eval_pass_at_k.py` | Runs pass@k evaluation (k=1,2,5) with Wilson CIs |
| `rex/harness.py` | Sim engine: `load_scenario()`, `run_plan()`, `is_safe()` |
| `rex/scoring.py` | Reward function (same deterministic judge) |
| `experiments/compute_pass_at_k.py` | pass@k calculator (unbiased estimator) |

### Scenario YAML format (what Beibei can browse)
```yaml
meta:
  id: 50-circleci-kubeproxy-iptables
  title: CircleCI kube-proxy/iptables version skew
  source: real
  urls: [https://discuss.circleci.com/...]
  failure_class: network_fault
topology:
  nodes: [kube-proxy, core-dns, rabbitmq, api, web]
  edges: [[kube-proxy, core-dns], [api, rabbitmq], ...]
root_cause:
  location: kube-proxy
  kind: version_skew
  hidden: true
  persistent: true
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

# Full 42-incident pass@k
python3 -m rex.eval_pass_at_k --model glm-5p2 --per-family 5 --seeds 3 \
  --conditions zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle

# Compute pass@k from existing data
python3 experiments/compute_pass_at_k.py
```

### Benchmark structure (SREGym-style, browsable)
```
scenarios/cidg/
├── 01-gcp-service-control.yaml      ← original (hand-authored)
├── 02-crowdstrike-cf291.yaml
├── ...
├── 30-singleton-node-notready.yaml
└── generated/
    ├── 40-redis-cache-flush.yaml     ← simple (8 total)
    ├── 41-billing-disk-fill.yaml
    ├── ...
    ├── 50-circleci-kubeproxy.yaml    ← cascade (14 total)
    ├── 51-datadog-systemd-cilium.yaml
    ├── ...
    ├── 70-facebook-bgp-backbone.yaml ← novel (10+ total)
    ├── 71-cloudflare-leap-second.yaml
    ├── ...
    └── 90-chronos-ntp-lease.yaml     ← novel (Ralph Loop)
```

---

## Pipeline 4: FIREBALL Cross-Domain Transfer

### What it produces
Converted D&D game trajectories in SRE format, for testing cross-domain
transfer learning (Claim 2).

### Data source
FIREBALL dataset: Zhu et al., ACL 2023, arXiv:2305.01528
HuggingFace: `lara-martin/FIREBALL` (CC-BY-4.0, 1,471 JSONL shards, 100K-1M rows)

### Python files
| File | Role |
|------|------|
| `experiments/ralph_outputs/E2/artifacts/fireball_fetch.py` | Downloads shards from HuggingFace |
| `experiments/ralph_outputs/E2/artifacts/fireball_schema.py` | Schema validation (17-key format) |
| `experiments/ralph_outputs/E2/artifacts/fireball_convert.py` | Converts D&D turns → SRE trajectory format |

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
python3 fireball_fetch.py --shards 5
python3 fireball_convert.py --input <shard.jsonl> --output fireball_sre.jsonl
```

---

## External Data Sources Summary

| Source | Type | Where used | URL |
|--------|------|-----------|-----|
| 19 real postmortems | Hand-extracted | Pipeline 2, 3 | See `catalog.md` for per-incident URLs |
| danluu/post-mortems | GitHub repo (700+ links) | Pipeline 3 (novel incidents) | https://github.com/danluu/post-mortems |
| FIREBALL D&D | HuggingFace dataset | Pipeline 4 (transfer) | https://huggingface.co/datasets/lara-martin/FIREBALL |
| SFT/DPO (ours) | HuggingFace dataset | Pipeline 1 (training) | https://huggingface.co/datasets/quantranger/infra-ops-incidents |
| HUD trajectories (ours) | Local + HuggingFace | Pipeline 2 (RLVR) | See `opensre-traj/out/HF_README.md` |
| SREGym | GitHub repo (90 problems) | Competitive comparison only | https://github.com/SREGym/SREGym |

---

## Infrastructure: Daytona + Modal (for efficiency)

Per Beibei's suggestion, switch to Harbor (Daytona + Modal) for faster inference:

### Modal (serverless GPU for training)
- Replaces HUD Tinker backend (currently 75-90s/step)
- H100 instances via Unsloth QLoRA
- Use for: 50-step RFT runs, same-scenario GRPO, multi-seed experiments

### Daytona (dev environments for eval)
- Spin up container with vLLM + repo
- Run pass@k locally without API latency
- Fixes the ablation stalling issue from overnight runs

### To switch:
```bash
# Modal for training
pip install modal
# Write train_rft_modal.py that swaps HUD Tinker → Modal GPU

# Daytona + vLLM for eval
pip install vllm
vllm serve Qwen/Qwen3-8B --port 8000
# Point eval_pass_at_k.py at localhost:8000 instead of HUD gateway
```

---

## Quick Reference: Which file does what

| File | Pipeline | What it does |
|------|----------|-------------|
| `opensre-traj/specs/*.json` | 1, 2 | 15 templated incident spec packs |
| `opensre-traj/generate.py` | 1, 2 | Generates SFT data + interactive corpus |
| `opensre-traj/generate_pathc.py` | 1 | Generates DPO pairs + rejections |
| `opensre-traj/lib_opensre.py` | 1, 2 | Shared: `render_trajectory()`, `TOOL_EVIDENCE` |
| `opensre-traj/hud_env.py` | 2 | HUD v6 interactive env (8 MCP tools) |
| `opensre-traj/train_rft.py` | 2 | GRPO/RFT training driver |
| `opensre-traj/train_rft_v2.py` | 2 | v2: deterministic judge, 10 tasks |
| `opensre-traj/real-incidents/catalog.md` | 2, 3 | 19 real postmortems (the seed) |
| `experiments/build_incidents.py` | 3 | Generates 62 YAML scenario specs |
| `rex/eval_pass_at_k.py` | 3 | Full pass@k evaluation pipeline |
| `rex/harness.py` | 3 | Sim engine: load, run, is_safe |
| `rex/scoring.py` | 2, 3 | Reward function (deterministic judge) |
| `experiments/compute_pass_at_k.py` | 3 | pass@k calculator |
| `tools_registry.json` | 1, 2 | 25 tools with trust tiers |
| `verify.py` | 3 | Verifiable reward — SLO check |
