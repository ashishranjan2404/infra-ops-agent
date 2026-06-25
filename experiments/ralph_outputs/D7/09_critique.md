# D7 — 09 Critique (honest)

## What a reviewer attacks first
1. **"This isn't training."** The strongest attack. The policy is a frozen LLM; D7
   manipulates the **in-context exemplar pool**, not weights. Mitigation: stated
   explicitly everywhere as a *proxy* for an RFT data-mix ablation. But a reviewer who
   wants gradient-trained evidence will (correctly) say this is a different experiment.
   The harness is built so the eval is identical for a real checkpoint — that's the
   honest path forward, but the current evidence is in-context only.

2. **Oracle-leak in the exemplars.** The exemplar shows the **gold fix tool**. That is
   a stronger signal than reward-only RFT distills. If cascade-only *had* helped
   cascade, a reviewer could attribute it to tool-copying, not learned generalization.
   (It didn't help here, so the attack is moot for this run — but it weakens any future
   positive result.) Labeled an upper-bound proxy.

3. **Under-powered → no result.** Smoke budget is 2 incidents × 2 seeds = 4 episodes
   per cell. Wilson CIs span ~[0.0, 0.49] / [0.51, 1.0] — wide enough that H1/H2 deltas
   are statistically indistinguishable from 0. The result is **direction-only**, and at
   this budget the direction is "flat." Honest, but not a publishable effect.

4. **Saturation hides the effect.** glm-5p2 is at **ceiling on simple (1.0)** and
   **floor on cascade (0.0)**. Transfer effects are unobservable at the extremes: you
   can't hurt a ceiling much or help from a floor with 4 samples. A mid-difficulty
   model (or harder simple / easier cascade incidents) would be needed to see transfer.
   This is the single biggest scientific weakness of the *run* (not the harness).

5. **`mixed` baseline leakage (now fixed) + pool-identity confound.** Eng-A caught that
   `mixed` didn't subtract eval names — fixed. The deeper confound remains: `cascade`
   and `mixed` pools are sampled independently, so they differ in *which* incidents,
   not only *which family*. A cleaner design would hold the non-cascade slots fixed and
   swap only family membership. Documented, not fixed (cap).

6. **std conflates incident-difficulty and sampling variance** (Eng-B). The reported
   `reward_std` is a coarse spread flag, not a formal trainability statistic.

## What's weak / missing
- No per-incident pass breakdown — a single easy incident can dominate a cell.
- No dedicated **over-diagnosis (trap-tool-on-simple) rate**; PSRE's failure mode is
  only *indirectly* captured via the judge's trap penalty in simple pass@1. With simple
  at ceiling, we have no evidence of over-diagnosis either way.
- No in-code wall-clock guard; safety came from sizing the config, not the code.
- Full-budget sweep not run (compute cap) — only the reduced smoke run.

## What's solid
- Config + harness are real, runnable, validated, deterministic, leakage-clean, and
  touch **no shared core file**.
- The real run executed live against glm-5p2 + the deterministic judge inside the cap
  and produced honest numbers.
- The negative/saturated result is reported as such, with the exact knobs
  (`n_eval_incidents`, `seeds`, `--model`) to make the experiment powered.

## Bottom line
**Deliverable: complete.** **Scientific verdict on the task question: inconclusive at
the delivered budget** — cascade-only exemplars neither measurably helped cascade nor
hurt simple, because glm-5p2 is saturated (floor on cascade, ceiling on simple) and the
budget is under-powered. The honest next step is a powered sweep on a mid-difficulty
model, which the shipped config supports without code changes.
