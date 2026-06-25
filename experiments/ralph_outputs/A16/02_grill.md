# A16 — Grill (5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PS), AAAI Reviewer (AR),
RL Engineer (RLE), DevOps Lead (DL).

## Round 1 — initial takes
- **SMR**: Validating that the *labeled* fix resolves the incident is exactly the
  reward-channel integrity check this benchmark needs. If `canonical_fix` doesn't
  actually clear the root in the sim, then any RL reward derived from "did the
  agent reach the canonical fix" is mislabeled. This is foundational, do it.
- **PS**: I care that "resolved" means the *root cause* is gone, not that the
  dashboards went green. Good — `is_resolved` already gates on `root_cleared`,
  not just SLO. So metric-masking won't pass. That's the SRE-correct definition.
- **AR**: A validator that just re-reads the YAML's own `assertions.fix_resolves:
  true` flag and echoes it back proves nothing. The contribution only holds if
  you EXECUTE the engine and compare. Show me the run.
- **RLE**: Apply order matters. `canonical_fix.steps` is an ordered list; if you
  reorder or skip steps you'll get spurious failures. Apply them verbatim, in
  order, then settle ticks before reading resolution.
- **DL**: How many scenarios, exactly? Parallel workers are mutating the dir.
  If you hardcode "42" you'll either miss files or report a stale count. Glob it.

## Round 2 — genuine disagreement (react by name)
- **AR → SMR**: You call this "foundational", but you're conflating two things.
  Confirming the fix resolves in the *sim* says nothing about whether the sim is
  faithful to reality. A green validator here is necessary, not sufficient. Don't
  oversell it as validating the benchmark — it validates internal consistency only.
  - **SMR rebuttal**: Fair, I'll scope the claim to "label/engine consistency,"
    not "real-world fidelity." But internal consistency is still a hard gate: a
    benchmark that's internally inconsistent is dead on arrival regardless of fidelity.
- **PS → RLE**: You say "apply steps verbatim." I disagree that's always right.
  Several scenarios are `persistent: true` with `reset_by` — in a faithful sim the
  upstream fix alone shouldn't restore SLO without a counter-reset. If the engine
  ignores hysteresis, then "verbatim apply passes" is actually hiding a missing
  engine feature. Don't let a green check paper over that.
  - **RLE rebuttal**: Agreed the engine doesn't implement hysteresis — I checked,
    `apply_action`/`is_resolved` never read `persistent`/`reset_by`. So the engine's
    verdict is the binding ground truth *for the engine*, and I'll explicitly flag
    that hysteresis is unmodeled rather than claim the scenario is "correct."
- **DL → AR**: You demand "show me the run" but you'd also fail me for editing a
  shared file to make a run pass. Those are in tension if the engine itself can't
  represent a scenario's SLO metric.
  - **AR rebuttal**: No tension. Run it, let it error/fail, and REPORT the error.
    A documented failure is a valid result. Editing `sim/engine.py` to swallow a
    KeyError would be the actual sin.

## Round 3 — synthesis
Consensus:
1. EXECUTE the engine; never trust the YAML's self-declared flag (AR, SMR).
2. "Resolved" = `root_cleared AND slo_ok`, the engine's existing definition (PS).
3. Apply `canonical_fix.steps` in order, settle `max(sustain_ticks)` (RLE).
4. Glob the live scenario set; report the actual count, don't hardcode 42 (DL).
5. Failures (wrong-target fixes, unmodeled SLO metrics, unmodeled hysteresis)
   are REPORTED with root cause, never silently patched in shared core (AR, PS).
6. Scope the claim to engine/label consistency, not real-world fidelity (SMR).
