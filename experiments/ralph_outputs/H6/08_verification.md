# H6 — 08 Verification

## Against the §01 success criteria

| Criterion | Met? | Evidence |
|---|---|---|
| Loads every scenario YAML | ✅ | 61 files discovered + loaded (10 `cidg/` + 51 `cidg/generated/`) |
| Checks schema | ✅ | reuses `sim.spec.validate` (closed-vocab kinds/edges/SLO + structural) |
| Checks the sim engine accepts it | ✅ | `World.from_spec` + `apply_action` + `run` per scenario |
| Exits nonzero on failure | ✅ | negative run → **exit 1**; no-match → **exit 2**; self-test asserts both |
| Exits zero when all valid | ✅ | full corpus → **exit 0**, `all_pass: true` in `ci_report.json` |
| CI-ready (clear exit codes) | ✅ | documented 0/1/2 contract + `ci_check.sh` wrapper + JSON artifact |
| RAN over all scenarios, real report captured | ✅ | `ci_report.json` (61/61) + `ci_report_negative.json` (0/3) committed |
| No shared-core edits | ✅ | only files under `H6/` written; `sim/*` imported read-only |

## Are the outputs real (not placeholder)?
- `ci_report.json` is the literal stdout/JSON of a real subprocess run over the on-disk corpus;
  re-running reproduces it deterministically (no randomness in the acceptance path).
- The 61 count matches `ls scenarios/cidg/*.yaml` (10) + `ls scenarios/cidg/generated/*.yaml` (51).
- `ci_report_negative.json` is a real run over real (broken) fixtures, demonstrating the gate
  actually fails — not a hard-coded "fail" string.
- Self-tests execute the real `main()` / `check_one()` and assert real exit codes (pytest: 6 passed).

## Independent sanity cross-check
The repo's own built-in `python3 -m sim.spec validate "scenarios/cidg/generated/*.yaml"` reports
`51/51 specs valid`, consistent with H6's schema stage passing those 51 files. H6 adds the engine
acceptance stages on top and extends coverage to the 10 curated `cidg/` scenarios as well.

## Conclusion
All success criteria met with reproducible evidence. The deliverable is a real, runnable,
CI-ready validator with a captured real report.
