# D11 — Honest critique

## The central weakness
The task literally asks for "variance across random seeds," and **I did not produce a real
seed-variance number** — because none was obtainable: the trainer never had seed control
and no multi-seed logs exist. A hostile reviewer says: "you measured the wrong variance and
called the real thing a blocker." That's a fair hit. My defense: fabricating 5 seed curves
would be worse (the brief explicitly forbids it), and I delivered the exact machinery
(valid patch + driver + analyzer + tests) that turns the blocker into one command on a
GPU box. But the gap is real and is the first thing an evaluator will attack.

## Statistical soft spots
- **Plateau std on 14–25 steps with k=5** is itself a noisy estimate of stability; with only
  5 plateau points the std has wide uncertainty I do not quantify (no CI on the std itself).
- **Within-step spread ≠ seed variance ≠ run-to-run variance.** I report three different
  variance axes; a careless reader could still conflate them despite the labels.
- **Cross-config std 0.0269** is a 3-sample std over confounded configs. It is nearly
  meaningless as an estimate (3 points, different model/n/trainer) and I say so, but it is
  the kind of number that gets quoted out of context. I almost cut it; kept it only because
  the grill (RLE) argued the config-robustness signal is real if labelled.

## Engineering soft spots
- The seed patch sets `HUD_ROLLOUT_SEED` on the assumption the HUD Tinker rollout sampler
  reads it. I did **not** verify that env var is actually honored by the HUD SDK — if it
  isn't, the patch seeds local RNGs but the rollouts may still be nondeterministic, which
  would *understate* true seed variance. This is an unverified assumption and a real risk.
- `loss` is `null` in every real log (the Tinker step result didn't expose it), so loss
  variance — arguably the cleanest stability signal — is unavailable. I work around it with
  reward, but a reviewer wanting loss curves gets nothing.

## What's genuinely solid
- The analyzer is correct, tested (10 cases incl. a hand-checked t-CI), dependency-free,
  and decoupled from the trainer.
- The patch is verified to apply cleanly and leaves the shared file untouched.
- The real numbers (plateau std, within-step spread, collapse check) are honest and
  reproducible from committed logs.

## If I had more budget
Apply the patch, run 5 seeds × 30 steps of the v2 config, re-run with `--seed-group`, and
report the real `mean ± 95% CI` on final reward — replacing "NOT MEASURED" with a number.
Also confirm `HUD_ROLLOUT_SEED` is honored, else find the SDK's true seed hook.
