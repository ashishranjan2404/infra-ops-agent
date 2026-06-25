# A11 — 08 Verification

## Success criteria (from 01_plan) vs result
| Criterion | Met? | Evidence |
|-----------|------|----------|
| 6 NEW YAMLs, parse, match existing schema | YES | Test 1 + Test 3, all parse and key-conform |
| 3 documented pairs | YES | manifest has 3 pairs / 6 files |
| Within pair: same failure_class + fix tool | YES | Test 2, asserted in generator |
| Within pair: different surface symptom | YES | Test 2, node count 1 vs 3, different services/SLO node/smoking guns |
| Machine-readable manifest | YES | `scenarios/cidg/generated/a11_pairs_manifest.json` parses |
| No existing file edited | YES | only new `a11-pair-*` YAMLs + new manifest; `registry.json` untouched |

## Are outputs real (not placeholder)?
Yes. The YAMLs are complete, schema-valid scenario definitions using only
failure classes, fix tools, and node kinds already present in the shipped
scenario set — so the existing loader and deterministic judge in `rex/scoring.py`
can consume them without modification. The manifest contains concrete filenames,
shared-root-cause records, and per-variant symptom descriptions.

## Reused-asset compatibility
- Fix tools (`restart_service`, `renew_certificate`, `increase_memory_limit`),
  node kinds (`service`, `lb`, `datastore`), and `<class>_active` sim toggles all
  appear in pre-existing scenarios (grep-verified), so no new sim primitive is
  introduced.

## Verdict
Deliverable meets all stated success criteria with real, validated artifacts.
The downstream transfer-eval *run* (train on A, test on B, score with the judge)
is a separate task and was intentionally not executed here; the manifest is the
contract that run would consume.
