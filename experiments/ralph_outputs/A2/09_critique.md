# A2 — 09 Critique (honest)

## What is strong
- The full 750-episode sweep **completed** with a faster/cheaper model (deepseek-v4-pro),
  0 errors, deterministic judge, in ~45 min — the exact deliverable the prior glm-5p2 run
  failed to produce (it died at 175/750).
- The result is scientifically clean and *survives the fair controls*: rex pass@1=0.893 beats
  best_of_n (raw-compute control, +0.586) and retry_realistic (outcome-feedback control,
  +0.580), and McNemar gives p<0.0001 on all pairs. The lift is not just "more compute".
- The `rex_vs_rex_no_oracle` split (91-pass-vs-0) is an *honest, load-bearing* finding: the
  lift is driven by the **oracle feedback**, not the bare tree. That is exactly the question
  the original `rex/ablation.py` was built to answer, now at n=150 with significance.

## What a reviewer will attack
1. **Oracle leakage is the whole story.** rex_no_oracle (0.287) is statistically
   indistinguishable from best_of_n (0.307) and retry_realistic (0.313). So on *this*
   substrate the Thompson tree contributes ~nothing once the gold-root/fix hint is removed —
   the headline "REx lifts every model" is really "an oracle hint lifts every model". This is
   a genuine weakness of the *method under test*, surfaced (not hidden) by the ablation; my
   job was to produce the number, and it does.
2. **Did the tree even expand?** I report best_score per condition but did NOT log per-run
   REx node counts in this artifact (the original `ablation.py` warns about <=2-node
   degenerate trees). I cannot fully rule out that rex_no_oracle ≈ best_of_n because the tree
   collapsed rather than because the signal was weak. A follow-up should dump `len(nodes)`.
3. **vLLM not delivered.** The task said "vLLM local OR cheaper API". No GPU/vLLM on this box,
   so I took the cheaper-API branch (honest, in-scope) — but a true *local* speedup was not
   demonstrated.
4. **Single faster model.** "REx lifts EVERY model" is asserted from one model here. This run
   adds deepseek-v4-pro as a data point; it does not by itself prove universality.
5. **Per-call speed was not the win.** deepseek under 16-way concurrency ran ~8-14 s/call
   (slower than its 2.3 s cold probe); the real win was *completion* via the harness, not raw
   latency. I do not oversell it as a speed result.

## Most honest one-paragraph summary
The 750-episode ablation now exists, completed, reproducible, with a cheaper model and paired
significance. The substantive result is two-edged: REx is dramatically better than every fair
control (good), but almost all of that advantage evaporates when the oracle root-cause/fix
hint is removed (rex_no_oracle ≈ best_of_n) — so the harness honestly shows the lift is the
*feedback content*, not the tree machinery. That is the kind of negative finding the brief
explicitly asked to be reported rather than buried.
