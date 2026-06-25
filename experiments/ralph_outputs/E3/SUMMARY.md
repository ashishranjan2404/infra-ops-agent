# E3 — SUMMARY

**Task:** Run Fireball-trained vs OpenSRE-trained vs zero-shot on 14 cascade incidents.

## Outcome: COMPLETED (Fireball arm blocked, not fabricated)

Built a real **3-way cascade comparison harness** and ran the two runnable arms on 14 cascade
incidents with the repo's P0 **deterministic** judge. The Fireball arm is a documented upstream
blocker — **no numbers fabricated**.

### Arms
| Arm | Model | Status |
|---|---|---|
| zero-shot | `Qwen/Qwen3-8B` (base, untrained) | runnable |
| OpenSRE-trained | `opensre-qwen3-8b-1e439a` (OpenSRE GRPO/RFT fork) | runnable |
| Fireball-trained | — | **BLOCKED**: no Fireball dataset/model (E2 + D8 empty) |

### Result (14 cascades, 2 seeds, 28 episodes/arm, deterministic judge, threshold 0.8)
| Arm | pass@1 | 95% CI | mean reward | std |
|---|---|---|---|---|
| zero-shot | 0.071 | [0.02, 0.23] | 0.454 | 0.293 |
| OpenSRE-trained | 0.107 | [0.04, 0.27] | 0.475 | 0.305 |
| Fireball-trained | BLOCKED | — | — | — |

OpenSRE shows a **small, non-significant lift** over zero-shot (CIs overlap, n=28) — consistent with
the prior "flat OpenSRE training" finding. Headroom check passed (base per-incident means span
0.0–0.85), so the null-ish result is a real signal, not a floor artifact. 56 episodes, 0 errors, 64s.

### Artifacts (all under `experiments/ralph_outputs/E3/`)
- `artifacts/eval_three_way_cascade.py` — the harness (selection, 3 arms, local roster registration,
  deterministic scoring, `--dry-run`).
- `artifacts/test_eval_three_way_cascade.py` — 6 network-free tests (all pass).
- `artifacts/result_three_way.json` — real run output.
- `artifacts/dryrun_three_way.json` — selection + reachability probe.
- `01..10` step files.

### Compliance
- **No shared core files edited** — the two gateway slugs are registered into a runtime-local roster
  copy (`ROSTER.setdefault`); `agent/models.py` and all `rex/`, `sim/`, `experiments/*.py` untouched.
- **No fabricated Fireball numbers.**

### Blocker
Fireball-trained model: no Fireball training data or forked model exists (upstream tasks E2/D8
produced nothing). The harness is ready to add it as a 4th arm the moment a Fireball slug exists.
