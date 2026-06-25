# D7 — SUMMARY

**Task:** Train on cascade incidents only — does it hurt simple, help cascade? Build the
cascade-only training config + an eval plan measuring simple vs cascade pass@1 transfer.

## Reframing (the key insight)
This repo is **code-as-policy over a FROZEN LLM** — no gradient steps in the local loop.
The faithful analog of "training data" is the **in-context exemplar pool**. So D7 =
exemplar pool drawn **exclusively from the cascade family**, then measure held-out pass@1
transfer to simple (OOD) and cascade (in-dist), versus `mixed` and `none` baselines.
This is an honest in-context proxy for an RFT data-mix ablation; the eval harness is
unchanged if a real checkpoint replaces the proposer.

## Deliverables (all task-namespaced; NO shared-core edits)
- `artifacts/d7_cascade_only.yaml` — cascade-only training config (the deliverable config).
- `artifacts/d7_train_eval.py` — train+transfer eval harness: exemplar injection,
  3 configs (cascade/mixed/none) x 2 eval families, deterministic-judge pass@1 +
  Wilson CI, hard train/eval leakage guard, `--dry-run` (zero-network), mini-YAML fallback.
- `artifacts/d7_results_smoke.json` — REAL reduced run (glm-5p2), real pass@1+CI.
- `artifacts/d7_results_dryrun.json` — zero-network wiring/leakage validation.
- `artifacts/d7_smoke.yaml` — reduced config used for the real run.

## Validation (07)
py_compile pass; YAML+fallback parity pass; dry-run schema pass; **zero leakage** pass
(incl. `mixed` after Ouroboros fix); split determinism pass; **real run exit 0 in ~4 min**
(within the 15-min cap).

## Result (smoke budget, n=4/cell)
- **simple pass@1 = 1.0** (ceiling), **cascade pass@1 = 0.0** (floor) for ALL three
  configs -> transfer deltas H1 = H2 = 0.0.
- Sub-threshold trend: cascade partial-reward mean ranks mixed (0.375) > none (0.188) >
  cascade-only (0.000) — weakly *against* "helps cascade," but sign-flips across runs
  -> noise on n=4.
- **Answer at this budget: inconclusive.** Cascade-only exemplars neither measurably
  helped cascade nor hurt simple, because glm-5p2 is **saturated** (floor on cascade,
  ceiling on simple) and the budget is under-powered. No over-diagnosis harm visible
  (simple stays 1.0).

## Honest verdict
Deliverable **complete** (real config + harness + tests, leakage-clean, no core edits).
Scientific result **negative/saturated** — the shipped config exposes
`n_eval_incidents`, `seeds`, `--model` to run a powered sweep on a mid-difficulty model,
which is the documented next step.
