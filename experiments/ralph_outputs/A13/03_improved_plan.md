# A13 — Improved Plan (post-grill)

## What changed vs 01_plan.md
1. **1 → 3 specs**, each isolating a difficulty axis (RLE's measurability point + PSRE's realism):
   - `80-multi-cert-poolleak.yaml` — independent coincidence, order-free (clean baseline).
   - `81-multi-rollout-cacheflush.yaml` — masking pair (bad_revision symptom hides cache_flush).
   - `82-multi-fdexhaust-cpustarve.yaml` — two faults on a shared blast radius (resource coupling).
2. **Secondary-fault block formalized** as `secondary_faults: [ {location, kind, severity, fix_tool} ]`.
   Chosen so each secondary fault has (a) a distinct location node, (b) its own SLO victim,
   (c) a canonical-fix step — so it is *immediately correct* the moment the engine patch lands
   (SMR's data-faithfulness burden; AAAI's construct-validity requirement).
3. **Engine patch is now a named deliverable** (`engine_multifault.patch`): injects every
   `secondary_faults[*].location` and makes `is_resolved` conjunctive (all fault locations cleared).
   This converts "mislabeled easy task" → real conjunctive task. NOT applied (no-edit rule).
4. **Test strengthened**: asserts 2 *distinct* fault locations, 2 SLO victims, 2 fix steps, AND
   that the primary single-fault path still runs/clears in the *unpatched* engine.

## Critiques accepted
- AAAI "construct validity / mechanism vs label" → accepted: ship the patch + author both faults as
  fully-resolvable (location + SLO + fix), so the mechanism is real and the data is patch-ready.
- RLE "separate the axes for ablation" → accepted: 3 specs, each one new axis.
- PSRE "at least one realistically coupled" → accepted as spec `82` (shared victim) and `81`
  (masking), without piling all axes into one spec.
- DOL "must validate today, no new tools" → accepted: closed-vocab only; both fixes use registry tools.

## Critiques rejected (with reason)
- PSRE "make one strictly order-DEPENDENT via a hard required edge between the two fault nodes" →
  **rejected for now**. Order-dependence on top of 2-fault + masking conflates axes (RLE's point) and
  the unpatched engine can't even express the second fault to enforce ordering, so the ordering
  assertion would be untestable today. Documented as future work in `09_critique.md`.
- SMR "raise pass@k k" → **out of scope**: eval-harness tuning is a different task; we only add data.

## Final deliverables
- 3 YAMLs in `scenarios/cidg/generated/` (numbers 80/81/82, confirmed unused).
- `artifacts/test_multifault.py`, `artifacts/engine_multifault.patch`.
- Validation + test evidence in `07_test_results.md`.
