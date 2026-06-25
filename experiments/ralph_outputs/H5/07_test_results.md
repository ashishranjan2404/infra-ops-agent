# H5 — 07 Test Results

All commands run from `experiments/ralph_outputs/H5/artifacts/`.

## T1 — generator runs, prints gate counts (PASS)
```
$ python3 gen_manifest.py
wrote .../sample_manifest.json
candidates=10  PROMOTE=2  HOLD=0  REJECT=8
  glm-5p2/zero_shot            p1=0.230 ci_lo=0.165 lift=+0.000 -> REJECT
  glm-5p2/best_of_n            p1=0.341 ci_lo=0.264 lift=+0.111 -> REJECT
  glm-5p2/retry_realistic      p1=0.349 ci_lo=0.272 lift=+0.119 -> REJECT
  glm-5p2/rex                  p1=0.897 ci_lo=0.832 lift=+0.667 -> PROMOTE
  glm-5p2/rex_no_oracle        p1=0.333 ci_lo=0.257 lift=+0.103 -> REJECT
  deepseek-v4-pro/zero_shot    p1=0.240 ci_lo=0.179 lift=+0.000 -> REJECT
  deepseek-v4-pro/best_of_n    p1=0.307 ci_lo=0.238 lift=+0.067 -> REJECT
  deepseek-v4-pro/retry_realistic p1=0.313 ci_lo=0.244 lift=+0.073 -> REJECT
  deepseek-v4-pro/rex          p1=0.893 ci_lo=0.834 lift=+0.653 -> PROMOTE
  deepseek-v4-pro/rex_no_oracle p1=0.287 ci_lo=0.220 lift=+0.047 -> REJECT
```

## T2 — manifest valid JSON, schema + count (PASS)
```
schema sre-degrees.promotion-manifest/v1
candidates 10
decisions {'REJECT', 'PROMOTE'}
```

## T3 — HTML parses, contains required markers (PASS)
```
HTML parsed OK, len=10911, markers present
# markers checked: barCell, schema string, sample_manifest.json,
#                   fetchSample, createElement("table"), t-PROMOTE
```

## T4 — served over HTTP, both resources 200 (PASS)
```
=== GET dashboard.html ===        200 10928b
=== GET sample_manifest.json ===  200 9471b
=== manifest content-type ===     Content-type: application/json
```
Confirms `fetch("sample_manifest.json")` resolves with the right content type when the
folder is served (the documented `file://` limitation is the only caveat).

## T5 — Node DOM-shim render over the REAL manifest (PASS)
Ran the page's actual `<script>` (defines `loadManifest`/`render`) against a minimal
document/fetch shim and drove it with `sample_manifest.json`:
```
n-tot = 10
n-prom= 2
n-hold= 0
n-rej = 8
err display = none
gatebox set = true
tables rendered children = 4   # 2 model headers + 2 tables
```
No JS exception; counters match the generator exactly; error box hidden.

## Fixes applied during testing
- Initial sanity check looked for the literal string `<table` which the page builds via
  `createElement("table")`; updated the check to `createElement("table")`. No code change
  to the artifacts was needed — the marker check was wrong, not the HTML.

## Result: 5/5 checks PASS.
