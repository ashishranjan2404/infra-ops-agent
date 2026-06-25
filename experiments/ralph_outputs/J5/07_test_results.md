# 07 — Test Results

## Live loop run (real agent output)
```
$ python3 experiments/ralph_outputs/J5/artifacts/run_case_study.py
mode=live-llm elapsed=10.55s -> .../J5/artifacts/trace.json
outcome=resolved clean_win=True best_iter=1 iters=2
```
PASS — real `gpt-5.5` proposer trace captured; 2 iterations; clean win.

## Spec test cases T1–T5
```
T1 fault_node=waf-engine category=bad_deploy
T2 trap resolved=False blocked=1
T3 fix resolved=True root_cleared=True
T5 artifacts valid JSON: ok
T4 live: any dx_correct=True outcome=resolved
ALL TESTS PASS
```
- **T1** scenario loads, root = `waf-engine`, category `bad_deploy` — PASS
- **T2** trap `scale_deployment(edge-proxy)` blocked by `is_safe` + unresolved — PASS
- **T3** fix `rollback_deployment(waf-engine)` resolves + clears root — PASS
- **T4** live trace has a diagnosis-correct iter and a terminal outcome — PASS
- **T5** both JSON artifacts parse — PASS

## Syntax / parse checks
```
run_case_study.py: syntax OK
parse OK: 01..06 + CASE_STUDY.md (all 7 docs)
```

## Errors hit and fixes applied
1. **First live run 400'd** on `https://api.anthropic.com/v1/messages`. Diagnosed:
   ```
   "Your credit balance is too low to access the Anthropic API."
   ```
   The default proposer `claude-haiku-4-5` is unreachable (credits exhausted).
   **Fix:** routed the proposer to a reachable HUD-gateway model via a custom
   `propose_fn` calling `propose(..., model="gpt-5.5")` — no core edit. Re-ran:
   live trace captured. (gpt-5.5 and gemini-3.1-pro reachable; deepseek-v4-pro
   returned empty.)
2. The deterministic-sim fallback was exercised on the first (failed-LLM) run and
   produced a valid artifact — confirming the honest-blocker path works before the
   gateway fix made the live path succeed.
