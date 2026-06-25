# A8 — 07 Test Results

All commands run from `/Users/mei/rl` with `python3` (3.13).

| # | Test | Result |
|---|------|--------|
| T1 | `build_heldout_split.py` runs, emits manifest+csv, assertion_pass | **PASS** (exit 0; 15 held-out, 17 contaminated) |
| T2 | `py_compile` both scripts | **PASS** ("compile OK") |
| T3 | `assert_no_overlap.py` on real manifest | **PASS** (exit 0; "zero overlap. strictly novel") |
| T4 | Negative control: inject `github_proxysql_fd_limit` | **PASS** (exit 1; flags exact-id + pair-overlap + company-axis) |
| T5 | `--strict-class` held-out ⊆ default held-out | **PASS** (default 15 ⊇ strict 13) |
| T6 | manifest.json + split.csv parse cleanly | **PASS** ("parse OK") |

## Key real output (T1)
```
training incidents: 34  | candidates: 32
HELD-OUT: 15  | contaminated: 17
assertion_pass=True violations=0
manifest sha256=3c8b7ee2eeb4bb7b...
```

## Key real output (T4 negative control)
```
FAIL: 4 overlap(s):
    ('github_proxysql_fd_limit', 'exact-id', 'github_proxysql_fd_limit')
    ('github_proxysql_fd_limit', 'pair-overlap', 'github_proxysql_fd_limit')
    ('github_proxysql_fd_limit', 'company-axis', 'github')
    ('github_proxysql_fd_limit', 'company-axis', 'proxysql')
exit=1
```

## Fixes applied during testing
- **Tier 2 hardened** mid-development: the original "company + extra meaningful
  token" rule let `launchdarkly_cold_cache` and `cloudflare_leap_second` slip into
  the held-out set (shared tokens were all on the STOP list). Changed Tier 2 to a
  hard company-axis exclusion; re-ran build → held-out corrected 18→15 and the
  guard confirmed zero overlap.
- Regenerated the on-disk manifest to the **default** (15) after a `--strict-class`
  run had left the 13-incident strict manifest on disk.

No outstanding failures.
