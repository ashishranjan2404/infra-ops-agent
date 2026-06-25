# A12 — 07 Test Results

## Commands run

### Generator (`--print`)
```
$ python3 experiments/ralph_outputs/A12/artifacts/build_curriculum.py --print
wrote .../curriculum_order.json  (51 incidents)

rank   diff  family     id
   0   0.90  unknown    cert-expire-leaf-sidecar
   1   0.90  unknown    fd-exhaust-leaf-shipper
   2   0.90  unknown    mem-leak-leaf-transcoder
   3   2.10  simple     billing_disk_fill
   ...
  48  17.00  cascade    github_network_partition
  49  17.00  cascade    launchdarkly_cold_cache
  50  17.00  cascade    slack_tgw_fd_exhaustion
```
Exit 0. Easy end = single-leaf incidents; hard end = real multi-service cascades.

### Validator
```
$ python3 experiments/ralph_outputs/A12/artifacts/test_curriculum.py
PASS  (51 incidents, 4 families, diff range 0.90..17.00)
```
Checks that passed:
- **coverage** — `len(order_easy_to_hard) == n == #yaml files`.
- **monotonicity** — `difficulty` non-decreasing across the ordered list.
- **split sanity** — every `family=="simple"` ranks below every `cascade`/`novel`.
- **determinism** — two consecutive generations produce byte-identical JSON.
- **uniqueness** — no duplicate incident ids.

### JSON parse check
```
$ python3 -c "import json;json.load(open('.../curriculum_order.json'))"
curriculum_order.json: valid JSON
```

## Issues found & fixed during testing
- **Moving incident count:** parallel Ralph workers were still writing new yamls into
  `scenarios/cidg/generated/` (count went 34 → 36 → 49 → 51 across runs). Fixed by
  making the generator idempotent and re-running it as the final step; the validator
  re-runs it too, so the artifact always matches the current scenario set.
- **Null-valued nested keys:** hardened all nested `.get()` calls with `(... or {})`
  so a present-but-null `meta`/`assertions` doesn't crash extraction (caught in
  ouroboros review, no live failure observed).
- **Unknown-family yamls:** newly added leaf scenarios not yet in `registry.json` get
  `family="unknown"` and fall back to `meta.id` — handled gracefully, no crash.

## Status: PASS — generator runs clean, output valid and deterministic.
