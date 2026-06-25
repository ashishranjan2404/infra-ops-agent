# A13 — Honest Critique

## What a reviewer will attack
1. **The faults aren't live in the shipped engine.** The strongest critique: today's repo engine
   injects only the primary `root_cause`; the second fault sits in a `secondary_faults` block that
   `sim.spec._build` silently drops. So in the *current* codebase these are single-fault scenarios
   wearing a multi-fault label. Honest status: the data + the conjunctive mechanism are real and
   verified on a patched copy, but the mechanism is delivered as a `.patch`, not merged. The
   no-edit-shared-core rule forced this; a follow-up task must apply `engine_multifault.patch`
   (and add the `is_resolved` conjunctive change) for the faults to be live and graded.

2. **No order-dependence.** Real masking multi-faults are often order-*coupled* (you must fix A
   before B is even diagnosable/fixable). My specs are order-free; `81` models masking only via
   `buried_under`, not via a hard dependency that prevents fixing B first. The engine cannot express
   the second fault at all today, so an ordering assertion would be untestable. Deferred — see below.

3. **Cascade depth is shallow.** Each spec is 4 nodes / 2 edges with each fault on its own 2-node
   chain. This keeps the two faults cleanly separable (good for ablation) but is less realistic than
   a deep shared-dependency graph where the two faults' blast radii overlap and interfere. A harder
   future spec would route both faults through one shared victim.

4. **Registry not updated.** `registry.json` has no entries for 80/81/82-multi (it's a shared file
   the brief forbids editing, and parallel workers may also touch it). Downstream tooling that reads
   the registry rather than globbing `*.yaml` won't see these three. Documented, deliberate.

5. **Severity/SLO tuning is by inspection, not search.** I chose severities (0.55–0.75) so both
   faults independently breach their SLO and both fixes are individually necessary, and verified the
   conjunctive property on the patched copy — but I didn't sweep to confirm robustness under the
   `chance.jitter`/`flap_prob` noise. A flaky-resolution check across seeds is missing.

## What's weak / missing
- No `paired_positive` siblings (single-fault scenes where the trap tool is correct) for the new traps.
- No deterministic-judge (`rex/scoring.py`) integration test showing a 2-fix trajectory scores
  higher than a 1-fix one — that needs the patch live, so it's blocked today.

## Honest blocker
The end-to-end "agent must fix both faults to resolve" grading is **blocked** on applying
`engine_multifault.patch` to shared core, which this task is forbidden to do. The deliverable
(valid multi-fault data + verified mechanism patch + passing tests) is complete; the *live grading*
is a one-commit follow-up.

## What's genuinely solid
Schema-valid, real, distinct-fault data; a verified conjunctive mechanism; trap and masking fidelity
preserved; zero regression to the existing 48 specs; no shared-core edits.
