# J7 — 01 Plan

## Objective
Run "the agent" against the live-cloud bench scenarios in `gcp-bench/` and
`linode-bench/`. Build/extend a runner that points the frozen-LLM agent at those
scenarios; run what is runnable offline; document any live-cloud blocker precisely.
Incur **no** cloud cost and disrupt **no** live resources. Do not edit shared core files.

## What these benches are (from inspection)
- `gcp-bench/` and `linode-bench/` are Tier-B **live RLVR** benches: 15 Kubernetes
  incident types (oom_kill, cpu_saturation, ... stuck_rollout), each with a
  Prometheus metric, an Alertmanager rule, a preq CRE rule (`scenarios/cre-*.yaml`),
  and a **gold runbook fix** (`registry.json: fix`).
- The existing loop (`stages/06_run_scenario.sh`) drives one scenario end-to-end and
  scores a 5-signal chain (metric breach → alert → CRE detect → action → recovery),
  but the *action it applies is the hardcoded registry `fix`*. **The LLM agent
  (`agent/llm.py`) is not in the loop yet.** gcp-bench has real prior results
  (`results/aggregate.json`, mean_reward 0.333) from a now-gone temp GKE cluster.

## Approach
Insert the agent as the **action-selection policy**: for each incident, build an SRE
prompt from the CRE rule + symptom, give the agent the candidate runbook actions (the
union of the 15 gold fixes = a real discrete action space), and have `agent.llm` pick
the fix. Score deterministically (chosen == gold) — no grading model, no cloud.

Two modes in one runner:
- `--dry-run` (offline, $0): use `agent.llm.build_request` (pure, no network) to prove
  the provider wiring assembles for every scenario, then score a deterministic baseline
  policy. Runs with no API key, no cloud.
- `--live-agent MODEL`: real `agent.llm.call(...)` action selection. The chosen kubectl
  command is **recorded, never executed** — applying it to a real cluster is the blocked
  downstream step.

## Files to create (all task-namespaced)
- `artifacts/agent_bench_runner.py` — the runner (gcp + linode).
- `artifacts/test_agent_bench_runner.py` — offline pytest.
- `artifacts/result_{gcp,linode}_dryrun.json`, `result_gcp_live_minimax.json` — outputs.

## Files to modify
None. The conceptual change ("agent chooses the fix") is delivered as a *new runner*
that reads the existing registries read-only; `stages/06_run_scenario.sh` is untouched.

## Dependencies
`agent/llm.py`, `agent/models.py`, the two `registry.json`s + `cre-*.yaml`. Python stdlib
+ `requests` (already used by agent). For live-cloud execution: gcloud/kubectl + a GKE/LKE
cluster + valid cloud credentials.

## Risks
- **Live-cloud blocker** (expected): temp hackathon GCP account may be gone → no cluster.
- LLM credit exhaustion on the live path (Anthropic key).
- Action space leakage: presenting all gold fixes makes selection easier than free-form;
  documented as a deliberate first-cut (Floor-4-style multiple-choice action space).

## Success criteria
1. A runnable runner that loads both benches and assembles a real agent prompt per scenario.
2. Offline dry-run produces real, deterministic, scored numbers for all 15×2 scenarios.
3. Live agent path proven to reach the model (real call), at least one model.
4. Cloud blocker documented precisely with the exact error. Zero cloud cost.
5. Passing self-contained tests. No shared core file edited.
