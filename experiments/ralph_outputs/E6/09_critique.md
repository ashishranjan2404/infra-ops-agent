# E6 — 09 Critique (honest)

## The headline weakness
**E6 produces no model metrics.** The scientifically interesting claim — "full > state-only
> action-only" (or whatever the ordering is) — is exactly what we cannot test. A reviewer
will say: you built the knife but never cut anything. That is fair. What exists is the
*instrument*, validated and ready, not the *experiment*.

## The blocker, precisely
1. **No real FIREBALL D&D corpus in repo.** `incidents.jsonl` referenced in
   `opensre-traj/README.md` is absent; nothing matches `*fireball*` (confirmed
   `experiments/results/P7_fireball_status.md`, task E2). The in-repo
   `opensre-traj/out/trajectories.jsonl` is the *target* (OpenSRE) domain, not the
   FIREBALL *source* domain — so it validates the transforms but cannot stand in for the
   cross-domain ablation.
2. **No fireball-trained slug** on HUD to evaluate the variants against.
3. Therefore the train→eval loop (emit variant → SFT/GRPO → `rex.eval_pass_at_k` +
   `rex.scoring` on cascades) cannot run. Unblock = a human provides Wenji's FIREBALL data
   + training setup.

## Attacks a reviewer would make (and my answer)
- *"The state/action split is arbitrary."* — Defensible but contestable: I put the agent's
  `thought` in the action channel (it accompanies the action), not a separate "reasoning"
  channel. A 4-way ablation (state / action / reasoning / fix) would be richer. Scoped out.
- *"action_only keeps `model_response` (a written diagnosis) — that's an output, leaking
  state."* — Defended: `model_response` is the *label/target* in all variants, not a channel
  being ablated; only the demonstrated *action sequence* is stripped from state_only. Still,
  a purist could argue the diagnosis encodes observed state. Judgment call, documented in 05.
- *"Empty trajectories after ablation."* — Possible for all-action / all-state records;
  treated as legal, downstream filtering out of scope. The harness surfaces it via mean_steps.
- *"Validated only on the target domain."* — True. The transforms are schema-driven, so they
  port to any record in this shape, but cross-domain quirks of real FIREBALL data are unseen.

## What's genuinely solid
The transforms are pure, deterministic, tested (16 cases incl. the partition invariant), and
run cleanly over 319 real records with a perfect step partition (2327+2327=4654). The blocker
is documented, not hidden, and **no metric was fabricated**. As a *data-engineering*
deliverable it is complete and correct; as a *scientific result* it is intentionally empty
and says so.
