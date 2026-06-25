# 05 — Ouroboros (self-critique as 3 engineers)

## Engineer A — "the security/safety auditor"
**Problems found:**
- A1. The guarantee is only as strong as the classification. If `tools_registry.json` is
  missing AND a new write tool exists not in the fallback set, `classify` returns
  `"unknown"` — but does the code still refuse to execute it? **Must verify unknown ⇒
  never executed.** (It is: `shadow_dispatch` only sets `executed=False`, never True, for
  anything; the read branch also doesn't execute. So unknown is safe.)
- A2. `PrometheusSource.fetch` does `urlopen` — what if someone passes a base_url whose
  `/metrics` 302-redirects to a POST-y endpoint? `urlopen` follows redirects. Low risk
  (we GET), but worth a note: scrape only trusted Prometheus.
- A3. The grep test (`subprocess` / `/ctl`) is necessary but a determined author could
  `__import__("subprocess")`. The structural guarantee is "no execution path is *written*,"
  not "execution is impossible by sandbox." Document this honestly.

## Engineer B — "the data/observability engineer"
**Problems found:**
- B1. `observe` only reads `app_requests_total`. The mesh also exposes `app_up`, latency
  histograms, upstream 2xx. A root-cause that's *slow* (not erroring) would show 0% 5xx
  and be missed. The fixture's payments fault is `error` mode, so victims appear — but a
  `slow` fault would silently produce "all nominal." **Gap: under-uses telemetry.** Accept
  as a known limitation for the slice; the report still carries `raw_metrics` so a richer
  diagnoser can be layered on.
- B2. Victim ranking by error rate puts the loudest (payments=98%) first, but in a true
  cascade the *root* may not be the loudest. The stub proposer guesses "last victim is
  root," which is a heuristic, not truth. Fine — diagnosis quality is the LLM's job, not
  the harness's; the harness just records it.

## Engineer C — "the test/CI engineer"
**Problems found:**
- C1. `test_runner_has_no_execution_imports` has a tautological first assertion
  (`... or True`). It's dead. The two real assertions (`subprocess`, `/ctl/...`) carry the
  weight — keep them, the dead one is harmless but should be acknowledged.
- C2. Tests import `shadow_runner` via `sys.path.insert`; if pytest is run from a different
  cwd the `REPO` walk could be wrong. Mitigated: `REPO` is computed from `__file__`, not cwd.
- C3. No test exercises `PrometheusSource` against a live endpoint — by design (no
  cluster). The parser is covered by the fixture, which is real Prometheus shape, so the
  live path's only untested line is the `urlopen` call itself. Acceptable; documented blocker.

## Final filtered spec (changes applied)
- Keep unknown⇒never-executed (A1) — already structurally true; assert it in test 3
  (`unknown != read`). ✅ implemented.
- Add honest notes for A2/A3/B1 in 09_critique (scrape trusted Prometheus; structural-not-
  sandbox guarantee; error-mode-only detection). ✅
- C1: leave the dead assert but call it out in 09. The load-bearing greps stay. ✅
- No code redesign needed — the slice holds.
