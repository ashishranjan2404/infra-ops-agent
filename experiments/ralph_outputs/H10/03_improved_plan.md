# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Eval is now three targets, not one.** `eval` (deterministic default),
   `eval-smoke` (fast sanity), `eval-frontier` (the cited baseline-vs-REx sweep).
   *Accepted RLE's critique* that burying the frontier sweep behind a flag hides
   half the project; *accepted SMR's* that the default must be the deterministic
   judge for reproducibility.
2. **`clean` hardened.** Scoped to `__pycache__`, excludes `.venv*`, `|| true`
   so it never aborts a make run. *Accepted PSRE's* foot-gun critique;
   *rejected* doing anything broader (no clearing `rex/runs/` or
   `experiments/results/` — those are expensive to regenerate and deleting them
   silently would be the very foot-gun PSRE warned about).
3. **train + train-smoke both kept, honestly labeled.** *Rejected REV's*
   suggestion to drop the heavyweight `train` — agreed with SMR that the
   *command* is itself a reproducibility artifact (it documents exactly how the
   open model is trained), even if the *run* needs HUD infra + a forked slug.
   Both carry "needs HUD_API_KEY" / `.venv-hud` notes.
4. **Self-locating REPO root** via `$(lastword $(MAKEFILE_LIST))` so the file
   works when copied into `artifacts/`. *Accepted DL's* portability point.
5. **`help` is the default goal**, self-documented from `## ` comments.

## Accepted / rejected summary
| Critique | Source | Verdict |
|---|---|---|
| Default eval must be deterministic | SMR | accepted |
| Expose frontier as first-class target | RLE | accepted |
| `clean` is a foot-gun | PSRE | accepted (scoped + venv-excluded) |
| Drop `train` (not reproducible) | REV | **rejected** (command = artifact) |
| Ergonomics: help/phony/overrides | DL | accepted |
| Self-locate repo root | DL | accepted |

## Unchanged
Targets still map 1:1 to real entrypoints; every recipe `cd $(REPO)` so module
imports resolve; validation is `make -n` on all targets + real runs of the two
cheap ones.
