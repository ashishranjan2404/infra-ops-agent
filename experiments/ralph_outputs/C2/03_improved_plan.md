# C2 — Improved plan (post-grill)

## What changed vs 01_plan.md

1. **Comparison metric is now hazard coverage, not JSON diff** (accepted SMR/AAAI/PSRE).
   The headline finding = "which hazards does each rule-set guard, via which features."
   `compare.md` will tabulate hazard coverage of: cascade-synth, baseline mixed-synth,
   hand-written `is_safe`. Raw rule JSON is secondary evidence.

2. **Held-out is cascade-only** (accepted AAAI). I evaluate cascade-synth and
   hand-written `is_safe` on the 6 held-out *cascade* incidents. I explicitly do NOT
   claim a win/loss by testing the cascade harness on leaf incidents.

3. **Model confound called out explicitly** (accepted PSRE/DVO). The baseline run used
   `claude-haiku-4-5`; Anthropic now 400s, so cascade-synth uses gateway
   `deepseek-v4-pro`. Findings are split into:
   - **split-driven** (hazard coverage) — the real, reportable result;
   - **model/wording-driven** (rule count, over-conditioning) — reported only as a caveat.
   Model is pinned via `C2_MODEL`.

4. **n=1 variance caveat** (accepted RLE). I report node scores and frame the conclusion
   as structural (which features get guarded), not as a performance benchmark. If time
   allows within the cap I note that a re-run could be done but is not required for the
   structural claim.

5. **Safety scope stated** (accepted DVO/PSRE): cascade-synth is a *probe*. It cannot
   learn leaf-only guards (`leak_restart`, `last_ready_node`, `replica_limit`) because no
   training example exhibits them — so it must not be deployed on leaf/node incidents.

## Critiques rejected (and why)
- **RLE: "subset by hazard may not hold; rule count may balloon."** I keep the
  *hazard-subset* prediction as the hypothesis but explicitly DECOUPLE it from rule count
  (I no longer predict the rule set shrinks in size). So this isn't rejected so much as
  the over-strong version (count shrinks) is dropped. The hazard-coverage subset claim
  stands and is exactly what the data tests.
- I reject the implicit suggestion to do many runs for a variance estimate: the compute
  cap (~15 min) and the structural (not benchmark) nature of the claim make n=1 +
  node-score reporting sufficient and honest.

## Concrete deliverables
- `artifacts/cascade_synth.py` (runnable, imports baseline machinery read-only).
- `artifacts/cascade_synth.json` (real run output).
- `artifacts/compare.md` (hazard-coverage table + held-out numbers + caveats).
