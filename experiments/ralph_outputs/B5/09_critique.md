# 09 — Honest critique

## What a reviewer attacks
1. **Small n → wide CIs.** 3 seeds × 2 incidents = n=6 per (model, condition). Baseline
   pass@1 = 0.167 has a Wilson CI of [0.03, 0.56] — the REx CI [0.61, 1.00] does *not*
   overlap it, so the lift is real at this n, but a reviewer rightly wants n≥30 before
   trusting the point estimates. The script scales with `--seeds`/`--scenarios`; only the
   15-min compute cap limited n here.
2. **2 of 5 models, 2 of 5 incidents.** The compute cap forced a subset. Anthropic-direct
   models (haiku, opus) are blocked (HTTP 400 / out-of-credits) and gemini-3.1-pro was
   dropped from the *real* run for latency (its first call stalled the buffered first
   attempt past several minutes). So the real numbers are gpt-5.5 + deepseek-v4-pro only.
   The headline lift may not generalize to the unrun models.
3. **REx hits a perfect ceiling (pass@1 = 1.000, std = 0.000) on both models.** That is
   *suspiciously* clean. On these two easy/cascade incidents with budget-3 and an oracle
   feedback path (default `rex_tree` uses the harness's privileged feedback), REx saturates.
   A skeptic says: the substrate is too easy / the oracle feedback is too strong, so pass@k
   can't discriminate among strong policies (no headroom). The honest fix is harder
   incidents (the `novel` family) and the no-oracle condition (`rex_no_oracle` /
   `realistic_feedback`) — both exist in `rex/eval_pass_at_k.py` and the script could add
   them, but that multiplies compute and would blow the cap.
4. **Baseline pass@k is degenerate for `no_temperature` gateway models.** baseline std is
   0.16–0.23, not 0 — so there *is* some sampling variation despite no_temperature (the
   gateway isn't perfectly deterministic). But it's small; baseline pass@5 (0.833 for
   deepseek) leans on the estimator's n<k extrapolation. pass@1 (the headline) is unaffected.
5. **pass@5 from n=6 with c≤1 leans on the estimator.** Printed n makes this transparent,
   but a careless reader could over-read pass@5.

## What's genuinely weak / blocked
- **Not the full 5×5 sweep.** This is a representative subset + a runnable full-roster
   script, per the compute-cap instruction — not the complete frontier table.
- **No `rex_no_oracle` / `novel`-family run** to show headroom, so REx's 1.000 ceiling is
   uncontested here.
- **gemini latency** wasn't root-caused (rate-limit vs reasoning); just routed around.

## What's solid
- The aggregation upgrade is correct and reuses the canonical estimators (single source of
  truth), unit-tested including the tricky n<k edge.
- The pass@1 lens delivered a real, non-obvious finding: **gpt-5.5 zero-shot has positive
  mean reward (0.35) but pass@1 = 0.000 — it never actually resolves an incident first-try**,
  which mean-reward-only reporting completely hides. That is precisely the value the task
  asked for.
- 0 errors, finished under the cap, no shared core touched.
