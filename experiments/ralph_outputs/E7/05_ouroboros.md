# E7 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "Schema purist"
**Problems found:**
- A1. `gold_target` falling back to `objective`/`goal` means a missing
  walkthrough silently produces a *weak* gold. The judge could pass trivially
  because answer and goal share words. → must be flagged.
- A2. `solved` for SRE uses `reward >= 0.5`, a magic threshold buried in code.
- A3. `available_actions` oracle handicap is recorded but never surfaced for the
  ablation the plan promised.

## Engineer B — "Integration realist"
**Problems found:**
- B1. The test imports `rex.scoring` via `sys.path` hacking; if run from a
  different cwd it could import the wrong module. Need robust repo-root resolve.
- B2. `mechanism_score`/`deterministic_judge` are *lexical* — passing on a
  synthetic fixture proves nothing about real transfer. The test name must not
  overclaim. (It's named `..._scorable_by_real_sre_judge` — scorable, not
  "transfers". OK, but document.)
- B3. No test asserts the oracle-handicap warning path actually fires.

## Engineer C — "Over/under-engineering auditor"
**Problems found:**
- C1. Four adapters when the task only strictly needs a generic one + one game
  example — but having 3 game domains is justified by "survey TextWorld/Jericho/
  ALFWorld" in the task, so keep. Not over-engineered.
- C2. `adapt_many` is unused by tests → minor dead surface, but cheap + in spec.
- C3. No CLI to actually *run a transfer eval* — but that needs real data
  (blocked). The scaffold is the correct stopping point.

## Resolution / final filtered spec
- **A1 accepted →** documented as an explicit caveat in 06/09 ("weak-gold
  fallback"); the fixtures all supply real `walkthrough_goal`/`expert_plan_summary`
  so the demo doesn't rely on the fallback. Keeping the fallback (don't crash on
  partial logs) but warn in docs.
- **A2 accepted (minor) →** threshold documented inline; left configurable-by-edit
  (won't touch shared core to add config).
- **A3 / B3 accepted →** validation already appends to `meta["warnings"]` when
  `action ∉ available_actions`; this is the ablation hook. Documented; a dedicated
  warning-path test is noted as a *known gap* (kept the suite at 12 focused cases).
- **B1 accepted →** test resolves `REPO_ROOT` via `os.path` relative to the test
  file, not cwd. (Implemented.)
- **B2 accepted →** test name says "scorable", and 06/08/09 state synthetic ≠
  transfer evidence.
- **C1/C2/C3 →** no change; scaffold scope is correct, live run is the documented
  blocker.
