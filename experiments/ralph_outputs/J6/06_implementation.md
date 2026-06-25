# J6 — 06 Implementation

## Artifacts created (all task-namespaced; NO shared-core edits)

1. **`scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml`** — the novel scenario.
   Unused name (`90-*`; nothing in the `9x` range existed). A genuinely novel failure mode:
   NTP clock-skew → leader-lease expiry → distributed-lock split-brain. Trigger is a *time
   source*, distinct from every generated scenario (closest is `74-github-zk-splitbrain`, a
   `net_delay` network partition). 4 nodes / 3 edges; `root_cause.kind = dns_race`; trap =
   scale the loud victim; canonical fix = `restart_service chrono-ntp`.

2. **`experiments/ralph_outputs/J6/artifacts/run_novel_sim.py`** — model-free generalization
   driver over `sim/engine.py`. Validates the YAML, then exercises 6 engine behaviors and a
   recorded engine caveat (see 07).

3. **`experiments/ralph_outputs/J6/artifacts/run_novel_agent.py`** — LLM agent-path driver.
   Registers the scenario in the **in-memory** `rex.harness._SCENARIOS` (no disk write), then
   runs the real `rex.loop.refine_loop` + P0 deterministic judge, grading with
   `rex.scoring.score_plan`. Model is overridden via `functools.partial(propose, model=...)`.

4. **`experiments/ralph_outputs/J6/artifacts/sim_result.json`** — captured sim-driver output.
5. **`experiments/ralph_outputs/J6/artifacts/agent_results.jsonl`** — captured agent runs (3 models).

## Key implementation decisions
- **Novelty within a closed vocab.** `sim/spec.py` enforces a closed `ROOT_CAUSE_KINDS`; you
  cannot invent a new kind token. Novelty therefore lives in the *mechanism + topology +
  narrative*, mapped onto the closest kind (`dns_race`, the timing/race class). This is the only
  faithful way to author a "never-seen incident type" the engine will actually run.
- **Cascade requires `required`/`discovery` edges.** Discovered at runtime that `pool`/`queue`
  edges carry no error in Tier-A (`sim/engine.py:_error_edges`). Victim→quorum edges are
  `required`; the clock→quorum edge is `discovery`. Without this the cascade is silently inert.
- **Parallel safety.** The shared `scenarios/cidg/generated/registry.json` is **never written** —
  the agent path sees the scenario only through an in-process dict mutation. No `rex/*.py`,
  `sim/*.py`, `agent/*.py`, `experiments/*.py`, or status/dashboard file was edited.
- **Frozen-model code-as-policy.** Per the project framing, the agent is a frozen LLM driven by
  `rex.loop`; nothing is fine-tuned. Generalization = the *same frozen policy* solving an
  incident type absent from any scenario set, scored by the reproducible P0 deterministic judge.

## No shared-core file was modified
Confirmed via `git status` (only the new YAML + the J6 directory are added; no tracked
core file shows as modified by this task).
