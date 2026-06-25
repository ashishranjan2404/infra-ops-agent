# D14 — 09 Critique (honest)

## What a reviewer will attack

1. **"34 canonical + 8 variants ≠ a clean 42-incident benchmark."** Fair. The *benchmark*
   surface is 34 distinct canonical incidents; the extra 8 are perturbed variants of
   synthetic bases 001-008, not new incident classes. The "42" is an RFT *task-set* size,
   achieved by adding within-class diversity — defensible for training, but a reviewer who
   reads "42-incident benchmark" as 42 *distinct root causes* will object. Mitigation: the
   task file's `kind`/`origin` fields make the composition explicit and auditable.

2. **No completed training curve.** The headline ask is "run RFT on 42." I delivered a
   *proven-runnable* config + a single-step live smoke (reward 0.659, spread 0.056), not a
   30-step learning curve. Under the ~15-min cap and shared-head contention a full run
   wasn't finished. So the strongest claim I can honestly make is "the 42-task pipeline
   runs and produces graded reward," not "RFT on 42 improves the policy."

3. **Curriculum is coarse.** Difficulty is the only ordering signal and it's a 3-value
   integer (3/4/5). True curriculum RL would re-rank by *measured* per-task reward/headroom,
   not a static label. The `curriculum: true` flag is a real easy->hard sort but not adaptive.

4. **`out:` writes into a shared dir.** `runs/train_rft_42.jsonl` lands under
   `opensre-traj/runs/` (append-only log). Low risk, but it is technically outside the
   task namespace; I archived a copy under `artifacts/smoke_run.jsonl` to keep evidence local.

5. **Model slug is a placeholder.** `opensre-qwen3-8b` isn't forked under this account
   (404 on resolve); the live smoke proceeded via the SDK's default-resolved head. A real
   run needs `hud models fork ...` first — documented, but an operator could miss it.

## What's genuinely weak / missing
- No held-out eval split wired (deliberately out of scope per the grill; `rex/eval_pass_at_k.py`
  exists separately) — so "did 42 beat 10?" is unanswered.
- Variant selection is "most-perturbed of bases 001-008" — arbitrary; a principled choice
  would pick variants that maximize evidence-framing diversity or reward variance.
- The reward's category term (0.35) is still the dominant, easily-maxed component flagged in
  the v2 design notes; expanding to 42 tasks doesn't fix that headroom problem.

## Honest bottom line
Real, validated deliverable: a 42-incident task file grounded in the actual corpus + a
runnable, config-driven GRPO launcher that (unlike the stock index-based runner) can
*express* all 42 — confirmed by a live rollout->reward->step smoke. The unfinished part is
an actual converged 42-task training run, blocked by the compute cap and transient shared-
backend contention, not by the artifacts.
