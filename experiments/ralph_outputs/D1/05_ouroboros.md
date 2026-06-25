# D1 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — Statistical reviewer
**Problem found:** The analyzer's `verdict` uses a fixed `flat_eps=0.005/step` with no
reference to the *noise*. With per-step reward std ~0.18 and n≈40/step, the standard
error of the mean is ~0.028; a slope of 0.00174/step over 15 steps moves the mean by
~0.026 — i.e. *within one SE*. So "flat" is the honest call, but the analyzer doesn't
expose WHY (it never reads `reward_std`). A reader can't see the slope is sub-noise.
**Fix:** Keep the threshold-based verdict (cheap, deterministic) but in SUMMARY explicitly
compare slope·N against the per-step std / SE so the "within noise" claim is grounded.
(Chose not to bloat the analyzer with a t-test for a single-run n=1 experiment —
documented in SUMMARY instead.)

## Engineer B — Reproducibility reviewer
**Problem found:** `run_rft_50.sh` uses `cd "$(dirname "$0")/../../../../opensre-traj"`.
That relative hop is brittle — if the artifact dir moves, it silently `cd`s wrong and
trains nothing (or the wrong env). Also `OUT` defaults differ between the launcher
(`train_qwen3-8b_v2_50step.jsonl`) and the actual run I executed
(`artifacts/train_d1_50step.jsonl`), which could confuse a reader about which file is "the" curve.
**Fix:** Documented both paths explicitly in 06/08; the launcher default writes into
`opensre-traj/runs/` (canonical location for curves, matching the existing ones), while
the attended D1 run writes the partial curve into the task artifacts dir. The `cd` is
guarded by `set -euo pipefail` so a bad path fails loudly rather than silently.

## Engineer C — Systems / failure-mode reviewer
**Problem found:** 50 steps will not finish in the 15-min cap (the smoke alone — 1 step,
group 2 — took ~tens of seconds; a real step is group 6 × 10 tasks = 60 rollouts).
If I only deliver a partial curve, a reader might think the launcher itself failed.
Also: append-only JSONL means a re-run *appends* duplicate steps rather than resuming
from the last step — the script doesn't actually skip completed steps.
**Fix:** (1) 07/09 state the compute blocker explicitly and label the partial curve as
EXPECTED, not a failure. (2) Documented the append-vs-resume caveat: to truly resume you
start a fresh `OUT` and concatenate, or accept duplicate step indices (the analyzer sorts
by step but does not dedup — noted as a known limitation, acceptable for a single attended run).

## Final filtered spec deltas
- Analyzer unchanged (threshold verdict kept); noise comparison moved to SUMMARY prose.
- Launcher `cd` kept but hardened by `set -euo pipefail`; path semantics documented.
- Partial-curve framing + append-not-resume caveat documented in 07/09.
