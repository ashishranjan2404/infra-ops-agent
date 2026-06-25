# B14 — Honest Critique

## What's weak
1. **It's an estimate, not a measurement.** The single biggest weakness: no token counts are
   logged in the result JSONs, so every dollar figure is modelled from `max_tokens` budgets, an
   assumed input size, an assumed output utilization (0.6), and per-condition call counts. A
   reviewer is right to discount absolute $ values. The mitigation is transparency, not accuracy:
   real prices and assumptions are flagged, and the script can swap in measured tokens the moment
   a run logs them.
2. **`retry_realistic` call count (2.3) is the one un-derivable number.** It early-exits on a
   clean plan, and the data doesn't record how many retries fired. 2.3 is a plausible expected
   value, not grounded in the runs. If real, it could be anywhere in [1, 4], shifting that row's
   $/incident by up to ~1.7×.
3. **Non-Claude prices are invented.** glm-5p2/deepseek-v4-pro/etc. are fictional slugs in this
   repo; their $/token are documented guesses. The *cross-condition* ranking within a model is
   invariant to the price (it scales uniformly), so the rex-vs-best_of_n finding is robust, but
   *cross-model* absolute $ comparisons are only as good as the assumed prices.
4. **Input-token size (1200) is a flat assumption.** Real prompts vary by incident complexity
   (cascade/novel scenarios have larger specs than simple ones). A flat number understates spread.
5. **Output utilization is global, not per-condition.** rex's later tree expansions may emit
   shorter refinements than a fresh zero_shot plan; a single 0.6 ignores that.

## What a reviewer attacks
- *"You concluded zero_shot is most cost-efficient — so REx isn't worth it?"* No: that's a
  floor-cost artifact (zero_shot is cheapest, leaves 77% unresolved). The real claim is the
  iso-cost one (rex 0.90 vs best_of_n 0.34 at equal 4-call budget). I put that front-and-center in
  08, but the bare table's "best by $/pass" line invites the misread — a reviewer will pounce.
- *"Your $/pass numbers have 2 decimals of false precision."* Fair — they're ratios of estimates.
  Labelled ESTIMATED, but the precision still over-signals confidence.
- *"Why not just log tokens?"* Correct objection. The right fix edits a shared core file
  (`eval_pass_at_k.py`), which the parallel-safety brief forbids — so it's documented as a
  follow-up, not done. A reviewer wanting measured cost is currently blocked on that.

## What's missing
- **Measured tokens** (the whole point) — blocked on a shared-file edit; documented in 06.
- **Latency/MTTR axis** — PSRE's point: for SEV1, wall-clock matters more than $; the metric is
  silent on it (that's task A9's domain). This metric is explicitly a *secondary efficiency axis*,
  not a training objective.
- **Confidence intervals on $/pass** — pass@1 has CI95 in the source JSONs; I propagate only the
  point estimate. The ratio's uncertainty isn't reported.
- **Frontier-model coverage** — only glm-5p2 and deepseek-v4-pro have pass@1 artifacts on disk;
  Claude/gpt/gemini rows aren't computed because no result JSON exists for them.

## Honest bottom line
A correct, runnable, unit-tested cost-efficiency harness that produces real pass@1-per-dollar
numbers from the real eval artifacts — with the major caveat that the cost half is *modelled*, not
measured, and clearly labelled as such. The headline finding (rex dominates best_of_n at iso-cost)
is robust to the pricing assumptions; the absolute dollar figures are not. Status: completed
deliverable, with the measurement upgrade documented and blocked only by the no-shared-edit rule.
