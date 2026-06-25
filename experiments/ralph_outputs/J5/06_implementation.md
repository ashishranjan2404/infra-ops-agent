# 06 — Implementation

## What I built (all task-namespaced; NO shared core file edited)

### `artifacts/run_case_study.py` (runnable)
Drives the **real** REx linear refine loop on `cloudflare_waf_regex` and dumps a
full structured trace. Key design points:
- Imports `rex.harness.load_scenario`, `rex.loop.{refine_loop, propose}`,
  `rex.harness.run_plan` read-only — does not modify them.
- **Proposer routing:** wraps `rex.loop.propose(sc, fb, model=PROPOSER_MODEL)` in a
  `propose_fn` passed to `refine_loop`, so I select the model **without** editing
  `rex/loop.py` (whose default `_SMALL_MODEL` is the now-unreachable Haiku). Default
  `gpt-5.5`, override via `J5_PROPOSER_MODEL`.
- **Deterministic fallback:** if the live LLM throws (network/credits), it traces
  the sim directly with the canonical trap and canonical fix, sets `live_error`, and
  still writes a valid artifact. Always exits 0, always prints `mode`.

### `artifacts/trace.json` (real captured output)
The live `gpt-5.5` run: `mode="live-llm"`, `outcome="resolved"`, `best_iter=1`,
2 iterations. Full per-iteration records (stated root cause, actions, blocked,
failed_checks, feedback). Produced in 10.55 s.

### `artifacts/trap_vs_fix.json` (sim demonstration)
The trap (`scale_deployment(edge-proxy)`) → blocked + unresolved; the fix
(`rollback_deployment(waf-engine)`) → resolved + root_cleared. Single, stable JSON
shape used by the case study's §3.

### `CASE_STUDY.md` (the deliverable)
Narrative grounded only in the two JSON artifacts: incident, step-by-step real
reasoning, the trap (two separate claims), the fix, outcome, and an honest
limitations section.

## Proposed core change (documented, NOT applied)
`rex/loop.py` hardcodes `_SMALL_MODEL = "claude-haiku-4-5"`, which 400s when
Anthropic credits are exhausted. A reasonable upstream change would be to read the
proposer model from an env var with the Haiku default:
```python
_SMALL_MODEL = os.environ.get("REX_PROPOSER_MODEL", "claude-haiku-4-5")
```
I did **not** edit the shared file; I achieved the same effect locally by passing a
custom `propose_fn`. Recorded here as a suggestion only.

## Commands
```
python3 experiments/ralph_outputs/J5/artifacts/run_case_study.py
# -> mode=live-llm elapsed=10.55s ... outcome=resolved clean_win=True best_iter=1 iters=2
```
