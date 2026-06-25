# D9 — 09 Critique (honest)

## Where a reviewer attacks
1. **The result is simulated, and the simulation bakes in its conclusion.** The
   Gaussian-band learner *guarantees* monotone-difficulty ordering wins. As
   evidence about the real Qwen policy, the comparison is worth ~zero — it proves
   a mechanism is *plausible* and the plumbing works, nothing more. This is the
   single biggest weakness and it is the direct consequence of the training
   blocker. Mitigation is honesty (loud labels) not a stronger claim.
2. **Static difficulty ≠ learning difficulty.** A12's signal is structural
   (topology size, trap booleans). The truly informative ordering for RL is by
   *reward variance under the current policy*, which is online and unavailable
   here. So even with real training, the A12 order is a reasonable prior but not
   the optimal curriculum.
3. **No forgetting term in the sim → rehearsal weighting is inert in the curve.**
   Rehearsal flows into the config (where a real trainer uses it) but the
   simulation can't demonstrate its value. A skeptic notes the harness can't
   actually motivate the rehearsal knob it ships.
4. **Single seed for curriculum/anti.** Defensible (deterministic orderings) but
   a reviewer wanting noise bars on every line won't get them.
5. **Band granularity is arbitrary.** 5–6 stages chosen by hand; no sensitivity
   analysis over `n_stages` or the LR/SIGMA/K sim params. Different params could
   shrink the curriculum-vs-random gap (though ordering should persist).
6. **Absolute rewards ~0.2 look like failure** unless you read the difficulty-
   mismatch caveat. Optics risk.

## What's missing / future work
- Replace `simulate_run` with real per-stage model rollouts graded by
  `rex.scoring.score_plan` (the seam exists). THIS is the experiment that would
  actually validate curriculum learning here.
- Online/self-paced curriculum: re-rank bands by measured reward variance each
  epoch (teacher-student), not just the static A12 prior.
- Add a forgetting/decay term so the rehearsal knob is testable in-sim.
- Sensitivity sweep over n_stages and sim params; seed bars on all curves.

## Honest bottom line
Deliverables (schedule, GRPO config, comparison harness, 10 green tests) are
real, deterministic, and correctly wired to A12. The *scientific* curriculum
claim is **not** established — it is blocked on real training and currently
stands only as a labeled mechanism demo with a falsifiable hypothesis and ready-
to-run infra. Status: completed deliverable, blocked downstream run.
