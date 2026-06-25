# 08 — Verification against success criteria

| # | Criterion | Met? | Evidence |
|---|-----------|------|----------|
| 1 | Observe real Prometheus text; derive cascade (root vs downstream) | ✅ | CLI run: victims `['payments','gateway','checkout']`, orders/db nominal; payments=98% 5xx flagged as root candidate |
| 2 | Agent proposes a plan; every write action recorded `executed: false` | ✅ | `test_write_actions_are_never_executed`: 2 write actions, all `executed is False` |
| 3 | `executed_count == 0` invariant; `ShadowViolation` if violated | ✅ | CLI `executed_count = 0`; `test_assert_no_side_effects_raises_if_executed` raises on a forged executed action |
| 4 | No execution imports (`apply_action`/`subprocess`/`/ctl`) in module | ✅ | grep scan + `test_runner_has_no_execution_imports` pass |
| 5 | End-to-end CLI run prints a real ShadowReport | ✅ | full JSON report printed (07) |

## Are the outputs real (not placeholder)?
- **Code:** real, runnable, `py_compile`-clean; 6 pytest cases pass.
- **Fixture:** real Prometheus text exposition matching `mreal/server.py::_metrics()`
  exactly (`app_requests_total{app,status}`, `app_up`, latency hist) — not a stub blob.
- **Report:** produced by an actual run over the fixture, not hand-written.

## What is verified vs assumed
- **Verified:** parsing, cascade derivation, read/write classification against the real
  `tools_registry.json`, the non-execution guarantee, nominal-vs-incident behavior.
- **Assumed / not verified (blocker):** behavior against a *live* injected fault in GKE,
  and the live-LLM proposer's diagnosis quality. The live path is the same code with the
  byte source / proposer swapped, so the safety property carries over by construction, but
  it was not exercised end-to-end against a real cluster (see 07/09).

## Verdict
Deliverable met: a real, tested shadow harness with a structurally-enforced "no action
executed" guarantee, grounded in `rex/loop.py` + `mreal`. The live-incident run is blocked
by cluster/LLM access, documented honestly.
