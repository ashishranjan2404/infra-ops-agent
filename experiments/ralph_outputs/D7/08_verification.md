# D7 — 08 Verification

## Success criteria (from 01) — checked
| Criterion | Status | Evidence |
|---|---|---|
| Cascade-only training config exists, valid | ✅ | `d7_cascade_only.yaml`, T2 parses under pyyaml + fallback |
| Eval harness exists, compiles, importable | ✅ | `d7_train_eval.py`, T1 PY_OK, module imports in T2 |
| Measures simple vs cascade pass@1 transfer | ✅ | result object has `cascade/mixed/none × simple/cascade` + `transfer` H1/H2 |
| Train/eval split with zero leakage | ✅ | T4 `NO_LEAKAGE_ASSERT: True` (incl. `mixed` after fix) |
| Deterministic, reproducible metric | ✅ | deterministic judge `score_plan`; split fixed by `Random(1337)` (T5) |
| Real run within ~15 min compute cap | ✅ | real reduced run exit 0 in **278 s** (T6) |
| Real (not placeholder) outputs | ✅ | `d7_results_smoke.json` from live glm-5p2 calls; `d7_results_dryrun.json` from real split |

## Are outputs real?
Yes. `d7_results_smoke.json` is produced by **live `agent.llm.call` to glm-5p2** scored
by the **deterministic judge** (`run_plan`+`score_plan`) — not hand-written. The
dry-run file uses a stand-in reward *only* for the reward value (clearly flagged
`dry_run: true`), but its split, leakage guard, and result schema are real.

## What the real numbers say (smoke budget)
- **simple pass@1 = 1.0**, **cascade pass@1 = 0.0** across all three exemplar configs.
- **Direct read on the task question:** at this budget, cascade-only exemplars neither
  measurably **helped** cascade (H1 ≈ 0; cascade stayed at 0.0 — floor) nor measurably
  **hurt** simple (H2 ≈ 0; simple stayed at 1.0 — ceiling). The signal is dominated by
  a **difficulty cliff**: glm-5p2 solves simple incidents and fails cascade ones
  regardless of in-context family.
- **reward_std on cascade is non-zero (up to ~0.38)** → there IS within-cell spread on
  cascade (some seeds get partial credit), i.e. the cascade family is *trainable* in
  principle; the exemplar lever alone just isn't enough to cross the 0.8 pass bar here.
- **Sub-threshold trend (leakage-fixed run):** cascade partial-reward means rank
  `mixed` 0.375 > `none` 0.188 > `cascade-only` 0.000 — i.e. cascade-only exemplars
  gave the *least* partial credit on cascade, weakly *against* "helps cascade." This
  flips sign across runs (n=4), so it is noise, not a finding — but it is the opposite
  of the naive expectation and worth stating honestly.

## Honesty about the result
This is a **negative/floor-and-ceiling result at the delivered budget**, not a clean
confirmation of "hurts simple / helps cascade." The deliverable (config + harness) is
complete and correct; the *scientific* answer is "under-powered + saturated at the
extremes — needs (a) more eval incidents/seeds to tighten CIs and (b) a model that
isn't at floor on cascade for the transfer effect to be observable." Both are
parameterized in the config. See 09 for the full critique.
