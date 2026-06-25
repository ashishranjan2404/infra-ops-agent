# G1 — Implementation

## What was actually built (all under experiments/ralph_outputs/G1/artifacts/)
1. **`sregym_adapter.py`** (~230 LOC, importable with no cluster/model/network).
   - Provider Protocols: `ObservationGatherer`, `TargetResolver`, `SREGymClient`
     (`# TODO(integration)` marks the seam SREGym binds at install).
   - Offline stubs: `StubGatherer`, `StubResolver` so the contract is testable.
   - `_prompt_from_observation` — builds the proposer prompt FROM a gathered observation
     bundle, NOT a leaked scenario spec (the AAAI validity fix from the grill). This also
     means the adapter has ZERO shared rex/* runtime dependency for prompt-building.
   - `default_propose(model)` — lazy closure; imports `agent.llm.call` + `rex.loop.parse_plan`
     only when actually proposing, so import stays hermetic.
   - `SREGymPlannerAdapter`: `build_diagnosis` (originating component first, downstream
     services labeled as victims), `translate_action`, `translate_plan` (emits both
     `out_of_action_space` and `partial_action_space`), `run_problem` (dry-run capable;
     submits only when `dry_run=False` and a client is bound).
   - `make_offline_adapter` — fully canned (no model) adapter for tests.
2. **`action_translation.json`** — the 12 remediation tools -> kubectl/MCP command
   templates. 9 expressible (restart/scale/rollback/patch-memory/rotate-logs/cordon/drain),
   4 inexpressible (`modify_network_policy`, `renew_certificate`, `clear_cache`,
   `failover_service`) each with an explicit reason. `{ns}/{kind}/{name}/{replicas}/{mem}`
   filled at run time by the resolver. The memory-limit JSON patch uses a `__MEM_PATCH__`
   sentinel so its literal `{}` braces never hit `str.format`.
3. **`test_sregym_adapter.py`** — 10 pytest cases (T1-T9 + partial-action-space). All pass.
4. **`run_plan.md`** — exact cluster procedure incl. the `--agent planner_rex` registration
   seam and paired-metric reporting.
5. **`RUN_PLAN_blocker.md`** — the documented blocker (infra + integration + semantic).

## Key design decisions (traceable to the grill / ouroboros)
- Prompt from observation bundle, not leaked spec (AAAI validity).
- Tool semantics static; resource binding dynamic via resolver (DOL).
- Inexpressible tools reported, never faked or silently zeroed (PSRE action-space gap).
- One propose, no offline refinement loop — refinement needs live feedback we don't have
  offline; the dead `budget` knob was cut (Ouroboros C1).
- Diagnosis labels downstream services as victims to avoid mis-localizing on cascades
  (Ouroboros B1).

## Shared-core safety
No shared core file edited. Runtime imports of `agent.llm` / `rex.loop.parse_plan` are
read-only and lazy. A proposed change to register a SREGym agent lives entirely as the
`planner_rex.py` snippet inside run_plan.md (in the SREGym repo, not ours) — nothing in
/Users/mei/rl/{rex,sim,agent,experiments}/*.py is touched.

## Relationship to prior task B15
B15 froze SREGym's PUBLISHED leaderboard numbers (a transcription artifact). G1 is the
complementary engineering deliverable: the harness/interface brief + the adapter that would
let OUR agent actually be run on SREGym. G1 produces NO scores of its own.
