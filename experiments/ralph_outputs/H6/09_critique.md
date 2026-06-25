# H6 — 09 Critique (honest)

## What a reviewer will attack

1. **Acceptance ≠ correctness.** The strongest critique: H6 proves every YAML *loads and runs*,
   not that the scenario is *solvable* or that the reward signal is meaningful. A scenario whose
   canonical fix never resolves the incident still passes H6 (it passes `apply_fix` because the
   action doesn't raise). This is by design — A16 owns the `fix_resolves` semantic audit — but it
   means a green H6 gate is necessary, not sufficient, for scenario quality. The split is defensible
   but must not be oversold.

2. **It largely wraps existing code.** `load_spec` + `validate` already exist in `sim/spec.py`,
   which even ships a `validate` CLI. H6's net-new value is: (a) engine-acceptance stages on top of
   schema, (b) the explicit CI exit-code contract (0/1/2 incl. no-match→2), (c) per-stage failure
   categorization, and (d) negative-path self-tests proving the gate bites. A skeptic could argue
   the repo could have just hardened `sim/spec._main`; H6 didn't, because the brief forbids editing
   shared core — so the logic lives in a task-namespaced wrapper instead. If adopted, the right
   long-term move is to fold H6's exit-code contract back into `sim/spec` (noted, not done).

3. **Corpus is all-green, so the positive run is low-information.** All 61 scenarios already pass;
   the interesting signal comes from the *negative* fixtures. I mitigated this by committing
   `ci_report_negative.json` and self-tests, but the headline "61/61" mostly demonstrates the
   corpus is healthy today, not that the validator is rigorous. The rigor is in the negative path.

4. **`except Exception` breadth.** Each stage catches broadly. I bounded it (record type, message,
   3 traceback lines; `Exception` not `BaseException`), but a subtle engine bug could be reported as
   a benign "stage failed" rather than surfacing loudly. For a CI gate that fails the build either
   way this is acceptable, but it trades a little diagnostic sharpness for sweep-completeness.

5. **Scope excludes live-cloud (chaos) fields.** H6 only exercises Tier-A. The `fault.chaos_*`
   fields that drive GKE/LKE are not validated against a real cluster. That's appropriate for a unit
   CI gate but means "scenario passes H6" says nothing about live-mesh executability.

## What's weak / missing
- No check that `instantiate`/`settle` ever actually fail in practice (the corpus never exercises
  those stages negatively); they're covered structurally but not by a dedicated failing fixture,
  because `validate()` catches the obvious engine-tripping cases first. A future fixture that passes
  schema but trips `propagate()` would harden those stages.
- No timing/performance budget (irrelevant at 61 scenarios, ~0.2s; would matter at 10k).

## Honest verdict
Solid, real, CI-ready acceptance gate that does exactly what the task asks and is honest about its
boundary with A16. Its rigor lives in the negative path and exit-code contract, not the all-green
positive run. Not over-engineered; arguably *could* have been folded into core, which the
parallel-safety rule correctly prevented.
