# B7 — Root-cause accuracy as a standalone metric — SUMMARY

## Goal
Report root-cause diagnosis accuracy on its OWN, decoupled from the graded
pass/fail reward in `rex/scoring.py`.

## Delivered
- `artifacts/root_cause_accuracy.py` — deterministic, hermetic metric + CLI.
  Grounded in `rex.scoring._stems` (the shipped judge's tokenizer) and the
  `_KIND_CATEGORY` taxonomy over scenario YAML `root_cause.kind`.
- `artifacts/test_root_cause_accuracy.py` — 13 unit tests, all green.
- `artifacts/run_output.txt`, `artifacts/rca_result.json` — real-data run.

## Results (real data: 197 HUD trajectories)
- Standalone root-cause accuracy: 0.213 (42/197).
- Decoupling: root-cause-correct disagrees with incident-resolved on 43.1% of
  records — the metric carries signal the pass/fail reward does not.
- Validity self-test: gold YAML descriptions through the classifier = 0.875,
  confirming classifier+mapping sound; low real-data number reflects agents'
  verbose multi-cause answers, not a metric bug.

## Constraints honored
- No shared core files edited; intended `rex/eval_pass_at_k.py` wiring documented
  as a proposal only. Fully hermetic (no LLM/network), reproducible.

## Known limitations (see 09)
Keyword classifier over-fires on "bad_deploy"; single-label scoring of multi-cause
narratives is lossy; decoupling uses a reward>=0.5 proxy for "resolved".
