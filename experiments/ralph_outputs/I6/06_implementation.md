# I6 — 06 Implementation

## Artifacts built (all under experiments/ralph_outputs/I6/artifacts/)
- `failure_taxonomy.py` — the analysis tool. Read-only imports `rex.scoring`; never
  edits any shared file. Two ingest paths + bucketer + report writer.
- `test_failure_taxonomy.py` — 7 pytest cases (precedence, tags, replay-path validation,
  real-data smoke + end-to-end).
- `failure_report.json` — machine-readable distribution (generated, real data).
- `failure_report.md` — human-readable report (generated, real data).

## How it works
1. **Probe ingest** (`rex/runs/diagnostic_probe_*.jsonl`, 12 rows): each row already
   carries `score`, `resolved`, `diagnosis_correct`, `failed_checks` → ingested directly.
2. **HUD ingest** (`rex/runs/hud/*.jsonl`, 35 files): the trace stores the
   `rex.score_plan` REQUEST payload `{plan, scenario, sim_result}` but NOT the score
   response. The tool **replays** `rex.scoring.score_plan` + `failed_checks` over the
   captured tuple using a `_Scenario` shim (exposes only the flattened fields the scorer
   reads: `correct_fix_tools`, `fault_node`, `trap_actions`, `gold_root_description`,
   `red_herring_hints`). The DETERMINISTIC judge is forced + injected, so re-scoring is
   fully hermetic (no network, no LLM). HUD episodes are deduped by
   `(scenario, root_cause, actions)` → 45 unique rollouts.
3. **Bucketing**: primary label by precedence `trap_taken > wrong_root_cause > no_fix >
   not_resolved`; secondary tags include `empty_plan`, `safe_abstain`, `zero_reward`,
   `attempted_trap_blocked` (trap present in plan but blocked by the safety harness).

## Real result (57 rollouts: 12 probe + 45 hud)
- Failure tail: **36 of 57** (21 clean wins). Strict zero-reward: **0** (graded reward,
  as predicted — partial credit dominates).
- Primary buckets of the 36 failed: **no_fix 22**, **wrong_root_cause 7**, **trap_taken 7**,
  not_resolved 0.
- Scenario hotspots:
  - `singleton_node_notready`: 20/20 failed, all `no_fix` — the model correctly diagnoses
    "last Ready node, cordon/drain unsafe" and SAFELY ABSTAINS (empty plan) → it never
    applies the canonical fix, so it loses the 0.25 fix + 0.45 resolved credit. This is
    the **safe-abstain-as-failure** mode: operationally correct (PSRE was right), reward
    scores it as failure (SMR was right). The taxonomy surfaces both via `safe_abstain`.
  - `oom_kill`: 6/6 baseline failures are `trap_taken` (scale_deployment / clear_cache on
    a per-process leak).
  - `gcp_service_control`: hidden-root cascade → `wrong_root_cause` (blames the downstream
    service-control victim instead of the api-gateway deploy) + 2 attempted-but-blocked traps.

## Shared-core safety
No file under `rex/`, `sim/`, `agent/`, or `experiments/*.py` was modified. The tool only
imports `rex.scoring` (pure functions, env-read only). Confirmed with `git status` scope.

## No proposed core-file change
This task is pure read/analysis; no `.patch` against a core file is needed.
