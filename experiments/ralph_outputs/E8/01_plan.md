# E8 — 01 Plan

## Objective
Answer "how much Fireball data is needed (1k? 10k? 50k trajectories)?" by designing a
**data-size sweep** over the Fireball-format trajectory corpus, building the
**sampling/subsetting harness**, and producing a **power-analysis estimate of required N**.
Deliver a runnable sweep harness + synthetic-fixture validation. Explicitly document the
Fireball-data blocker. **Do NOT fabricate scaling curves.**

## What "Fireball format" is in this repo
Established by reading the repo (not assumed):
- `opensre-traj/SCHEMA.md` + `lib_opensre.py` mirror FIREBALL's
  `state_before → fix → state_after` trajectory spine.
- The materialized corpus is `opensre-traj/out/trajectories.jsonl`:
  319 records, 34 incident families, difficulty {3:100, 4:201, 5:18}, mean 14.6 steps.
  Each record: `trajectory_id, incident, scenario_id, difficulty, alert, evidence,
  answer, remediation, trajectory[]` (alternating assistant/tool).
- Prior status: `experiments/results/P7_fireball_status.md` documents the *original*
  FIREBALL D&D SFT corpus (`incidents.jsonl`) and the fireball-trained model slug are
  **not in this repo** — that is the standing blocker.

## Approach
1. **Reader** tolerant of the Fireball record shape (id / family / trajectory keys), with
   de-dup and bad-JSON guards.
2. **Stratified subsetter**: deterministic N-sized draws that preserve family×difficulty
   distribution and are *nested* (subset(N1) ⊂ subset(N2)) so a sweep reuses rollouts.
3. **Power analysis**: per-arm N to detect a mean-reward effect δ given per-record reward
   sd (use observed Claude-half sd ≈ 0.20–0.23 from `opensre-traj/DATA.md`). Normal
   approximation with an inline inverse-normal (no scipy).
4. **Sweep driver**: for each (N, seed) draw a subset, write a manifest, and — only if a
   real fit callback (trainer/evaluator) is supplied — record (N, score). With no
   callback, emit subsets + power analysis and mark the run BLOCKED. A learning-curve
   fitter requires ≥4 real points or it returns None (anti-fabrication guard).
5. **Synthetic fixture** (`make_fixture.py`): 2k Fireball-shaped records with NO score
   field, to validate the harness at scale without the real data.
6. **Tests** (`test_fireball_sweep.py`, pytest): reader, subsetter determinism/strata/
   nesting, power monotonicity + known value, and the two anti-fabrication guards.

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/E8/artifacts/fireball_sweep.py`
- `experiments/ralph_outputs/E8/artifacts/make_fixture.py`
- `experiments/ralph_outputs/E8/artifacts/test_fireball_sweep.py`
- subset manifests under `.../E8/artifacts/sweep_manifests/`

## Dependencies
Python 3 stdlib + pytest only. No scipy/numpy (inverse-normal is inlined).

## Risks
- The real corpus is far below 1k (it is 319). The sweep's headline N values
  (1k/10k/50k) cannot actually be exercised on real data → must be a documented
  blocker, not a faked curve. Harness must degrade honestly (cap at corpus size).
- Reward sd is taken from a different (HUD eval) measurement than SFT-data scaling; the
  power N is an *estimate*, labelled as such.

## Success criteria
- Harness reads the real corpus, profiles it, and runs a sweep that caps at corpus size.
- Power analysis returns sensible, monotone N estimates with a known-value test.
- Fixture sweep exercises 100→2000 with strata preserved.
- All pytest tests pass.
- No score/curve fabricated; blocker documented in 07/09.
- No shared core file touched.
