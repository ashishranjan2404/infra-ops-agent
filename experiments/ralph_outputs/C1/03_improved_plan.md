# 03 — Improved Plan (post-grill)

## What changed vs 01

1. **Override mechanism is now explicit and verified (RLE, accepted).**
   Do NOT monkey-patch `COMPLEXITY_LAMBDA`. Define `score_with_lambda(rs, ex, lam)` in the
   driver and pass it as `evaluate=` to `thompson_search`. Add a test asserting it equals
   `harness_synth.train_score(rs, ex)` exactly at `lam == COMPLEXITY_LAMBDA` (0.003). This
   is the trust anchor — without it the sweep is unmoored from the real reward.

2. **Report false-allows separately on BOTH splits (PSRE, accepted).**
   Every sweep row now carries `train_false_allow`, `heldout_false_allow`,
   `heldout_false_allow_rate`, not just accuracy. Accuracy alone hides the safety-critical
   axis.

3. **Label the operator on every result (SMR/AAAI, accepted).**
   The JSON and the docs state `mode: offline|real` on every row. Offline numbers are
   presented as the *lambda response of a fixed weaker operator*, NOT as `harness_synth.py`'s
   real haiku output. This is the honest scope.

4. **Held-out is reported, never selected (AAAI, accepted).**
   No "best lambda" is chosen by held-out accuracy. The deliverable is the curve + an
   observation of where false-allows start rising.

5. **Empty-collapse is a headline, not a footnote (DevOps/PSRE, accepted).**
   Explicitly check and call out the lambda at which the rule-set collapses to empty
   (harness silently disabled → all should-block actions false-allowed).

## What I rejected and why

- **SMR's implication that offline numbers are nearly worthless** — rejected as too strong.
  The offline operator is weaker in *absolute* rule count, but the *lambda response* (how
  n_conditions and false-allows move as lambda grows) is exactly what the task asks for and
  is *cleaner* without the LLM confound. I keep offline as primary but bound its claim.

- **AAAI's "single seed = anecdote, need many seeds" for the offline run** — partially
  rejected. The offline operator is *deterministic* (greedy argmax over a fixed atom set),
  so seed has no effect on it; multi-seed averaging is meaningless for offline. I note this.
  Multi-seed WOULD matter for the real haiku operator, which is blocked anyway.

## Final shape (unchanged from 01 otherwise)
Driver `lambda_sweep.py` (offline default + `--real`), full offline sweep JSON, real-subset
JSON or documented blocker, and `test_lambda_sweep.py`.
