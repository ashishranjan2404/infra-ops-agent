# E3 — 08 Verification

## Success criteria (from 01) vs reality
| Criterion | Status | Evidence |
|---|---|---|
| Harness selects exactly 14 distinct cascade incidents | ✅ | test #1 + dry-run list (14 names, all family=cascade) |
| Runs the runnable arms end-to-end with deterministic judge | ✅ | 56 episodes, 0 errors, `result_three_way.json` |
| Zero-shot arm = same base model OpenSRE was forked from | ✅ | both arms `Qwen/Qwen3-8B`-family; zero_shot=`Qwen/Qwen3-8B`, opensre=`opensre-qwen3-8b-1e439a` |
| OpenSRE arm run if reachable | ✅ | reachable (200), 28 real episodes |
| **No fabricated Fireball numbers** | ✅ | arm `status=blocked`, `roster_key=None`, no metrics emitted; table prints `BLOCKED` |
| Fireball blocker documented | ✅ | 06 + 09 + `arm_status.fireball_trained.reason` in JSON |
| No shared core files edited | ✅ | `git status` shows only new files under `E3/`; roster registered via runtime `setdefault`, file untouched |
| Tests pass | ✅ | 6/6 pytest |

## Are the outputs REAL (not placeholder)?
- `result_three_way.json`: real — 56 episodes, real deterministic rewards, real Wilson CIs,
  per-incident means present, `elapsed_s=64.2`, `n_errors=0`.
- Both gateway slugs verified reachable with live 200 responses (probe text captured).
- The deterministic judge (`rex.scoring.score_plan`) is the repo's shipped reproducible scorer.

## Result (descriptive — CIs overlap, no significance claimed)
- **zero-shot** (base Qwen3-8B): pass@1 **0.071** [0.02, 0.23], mean reward **0.454**, std 0.293.
- **OpenSRE-trained**: pass@1 **0.107** [0.04, 0.27], mean reward **0.475**, std 0.305.
- **Fireball-trained**: **BLOCKED** — no data/model.

OpenSRE shows a **small positive lift** (+0.036 pass@1, +0.021 mean) over zero-shot on these 14
cascades, but the **95% CIs overlap heavily** at n=28/arm — consistent with the prior "flat
OpenSRE training" finding. This is reported as a directional, non-significant result.

## Verdict
The deliverable — a runnable 3-way comparison harness, a real 2-arm run on 14 cascades, and a
documented Fireball blocker with zero fabricated numbers — is met. **COMPLETED.**
