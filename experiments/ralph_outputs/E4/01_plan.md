# E4 — 01 Plan

## Objective
Answer: **does specialising a policy hurt it on simple incidents?** Specifically,
compare a **Fireball-trained** policy vs an **OpenSRE-trained** policy on the 8
simplest incidents and measure per-incident regression ("does it hurt?").

## Reality check (front-loaded)
- **Fireball model: BLOCKED.** No FIREBALL training corpus and no fireball-trained
  slug exist in this repo (confirmed: `experiments/results/P7_fireball_status.md`,
  no `*fireball*` artifact, not in `agent/models.py` ROSTER).
- **OpenSRE-trained slug: also not pushed.** `opensre-traj/train_rft.py` is the GRPO
  trainer, but Wenji's run was never pushed (CLAIMS_EVIDENCE.md).
- Therefore the *trained-vs-trained* numbers cannot be produced tonight without
  fabrication. Per the brief, I deliver: real plan + spec + a **runnable comparison
  harness** on the 8 simple incidents + a real run with available frozen models as
  clearly-labelled STAND-IN policies + a documented Fireball blocker.

## Approach
1. Pin the 8 simplest incidents (subset of the 12-member `simple` family from
   `rex.harness.scenarios_by_family()`).
2. Build a self-contained driver `compare_simple8.py` that, for any two roster
   slugs, runs each zero-shot N seeds/incident, grades with the **P0 deterministic
   judge** (`rex.scoring.score_plan`), and reports per-incident pass@1 + the
   delta(B−A) + a "hurts" flag + an overall verdict.
3. Run it with `glm-5p2` vs `minimax-m3` (the two Fireworks models that return
   content) as stand-ins to prove the pipeline and emit real numbers.
4. Document the blocker so a human can drop in the real slugs and re-run unchanged.

## Files to create (all task-namespaced — NO shared-core edits)
- `experiments/ralph_outputs/E4/artifacts/compare_simple8.py` — the harness.
- `experiments/ralph_outputs/E4/artifacts/test_compare_simple8.py` — offline tests.
- `experiments/ralph_outputs/E4/run_standin.json` — real run output.
- `01..10 + SUMMARY.md + result.json`.

## Dependencies
- Frozen REx primitives (imported, never modified): `rex.harness.load_scenario /
  run_plan / scenarios_by_family`, `rex.loop.build_prompt / parse_plan`,
  `rex.scoring.score_plan`, `experiments/compute_pass_at_k` (pass_at_k/wilson/binary).
- Keys from `~/.zshrc` + repo `.env` (ANTHROPIC/FIREWORKS/HUD).

## Risks
- Anthropic key 400s (out of credits) and gateway models return empty content →
  only Fireworks models usable as stand-ins. Acceptable: stand-ins only prove the
  pipeline; the scientific claim stays BLOCKED on the trained slugs.
- 8 incidents × 2 policies × few seeds is low statistical power → report Wilson CIs
  and treat per-incident deltas as directional, not significant.

## Success criteria
- Harness imports frozen primitives, edits no shared core file.
- Offline tests pass (8 pinned incidents are real `simple`-family members; summarize
  math correct).
- A real run completes with 0 fabricated numbers and an honest BLOCKED verdict on
  the actual scientific question.
