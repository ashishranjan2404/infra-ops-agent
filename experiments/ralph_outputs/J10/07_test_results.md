# J10 — Test Results

## Run 1 (first draft) — FAILED, guard caught a real issue
```
$ python3 check_readiness.py readiness_gaps.json --md lessons_from_production.md
...
FAIL — 1 problem(s):
  - fabricated-prod phrasing in md: 'deployed to production'
EXIT=1

$ python3 -m pytest test_readiness.py -q
2 failed, 5 passed
  FAILED test_no_fabricated_prod_phrasing_md
  FAILED test_markdown_has_required_sections
```
**Cause.** Section-0 sentence "has not been deployed to production" tripped the
banned-substring guard. This is the integrity guard working — it flags fabricated-prod
phrasing even inside a legitimate negation, forcing unambiguous wording.
**Fix.** Reworded to "has not run in a live production environment."

## Run 2 (after fix) — PASS
```
$ python3 check_readiness.py readiness_gaps.json --md lessons_from_production.md
J10 readiness — No production deployment has occurred; this is a deployment-readiness analysis. ...
Lessons: [L1] [L2] [L3] [L4]
Gaps (all targets NOT YET MEASURED): [G1] [G2] [G3]
Checklist: 1/8 done
OK — all readiness invariants hold; no fabricated production claims.
exit=0

$ python3 -m pytest test_readiness.py -v
test_json_parses_and_schema PASSED
test_three_required_gaps PASSED
test_grounding_paths_exist_and_nonempty PASSED
test_acceptance_gates_labeled PASSED
test_no_fabricated_prod_phrasing_md PASSED
test_markdown_has_required_sections PASSED
test_verify_clean PASSED
7 passed in 0.01s
```

## What the tests actually validate
- **Schema**: required top-level keys present; task_id == J10.
- **Required gaps**: ids == {G1,G2,G3}; names contain "distribution shift" / "shadow" / "mttr".
- **Grounding existence + non-emptiness**: all 4 lessons + 3 gaps cite real, non-zero-byte
  files under `/Users/mei/rl` (the anti-fabrication backbone). Verified the cited
  D13/A16/A9 SUMMARYs, result/validation JSONs, and `rex/scoring.py` all exist.
- **Acceptance-gate labeling**: every gate begins `TARGET — NOT YET MEASURED:`.
- **No fabricated-prod phrasing** in the markdown (literal + regex MTTR-percentage guard).
- **JSON↔MD agreement**: every G1–G3 and L1–L4 heading present in the markdown.

## Shared-core check
```
$ git status --porcelain rex sim agent
(empty)
```
No core files modified. All artifacts are new files under the J10 task directory.
