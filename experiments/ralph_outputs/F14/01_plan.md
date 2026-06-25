# F14 — 01 Plan

## Objective
Produce a real, deliverable 15-minute talk outline for SRE-Degrees (the opensre / REx
incident-response RL environment), suitable for a conference / AAAI-style presentation if
accepted. Slide-by-slide: title + key point + timing, grounded in the **actual** project
narrative and results (not aspirational claims).

## Audience & constraints
- AAAI / ML-research audience: they reward (a) a real verifiable task, (b) honest ablations,
  (c) clear novelty, and they will attack overclaiming.
- 15 minutes spoken ≈ ~13–14 min of slides + ~1–2 min buffer for transitions/Q&A handoff.
  Rule of thumb: ~1 min/slide average, faster on setup, slower on the 2–3 result slides.
  Target 16–18 slides so no single slide exceeds ~75s.

## Approach
1. Mine the two canonical narrative sources for ground-truth numbers:
   - `ARCHITECTURE.md` — system, the reward function, the REx-lift table (0.63–0.81 → 0.86),
     curriculum (~0.19–0.42 → 0.59–0.71), two-tier reality contract.
   - `docs/headline_insights.md` — the **honest** version: env band 0.20–0.50 with variance,
     searched verifier (14→3 rules, 0.90 vs 0.95 held-out), and the ablation that shows REx's
     headline lift was largely oracle-feedback leakage (REx 0.25 ≈ zero-shot 0.24 once the
     root-cause hint is stripped).
2. Resolve the tension between the two: the talk's spine must be the **defensible** claims —
   the verifiable environment and the *searched* safety verifier — and must present the
   ablation as a feature (rigor), not bury it. This is the single most important design choice.
3. Lay out an arc: hook (the cascade that fools frontier models) → why existing benchmarks
   fail → our environment → the reward (anti-gaming) → the searched verifier (the real
   novelty) → results with the honest ablation → two-tier reality contract → limitations →
   contributions/close.
4. Write the outline as a real artifact (markdown) with per-slide timing that sums to ~15 min,
   plus a one-paragraph speaker-note per slide and a backup-slides appendix for Q&A.

## Files to create
- `experiments/ralph_outputs/F14/artifacts/talk_outline_15min.md` — the deliverable outline.
- `experiments/ralph_outputs/F14/artifacts/timing_check.py` — validates the timing budget
  sums to the 15-min target and flags any over-long slide.
- The 10 step files + SUMMARY.md + result.json.

## Dependencies
- None external. Pure content + a tiny stdlib timing-validator script (Python 3.13).

## Risks
- **Overclaiming**: pulling the rosy 0.86 table without the ablation caveat would get torn
  apart by a reviewer. Mitigation: ablation is its own slide, framed as "we stress-tested our
  own headline."
- **Timing drift**: 18 slides in 15 min is tight. Mitigation: timing_check.py enforces budget.
- **Two competing narratives** (ARCHITECTURE optimistic vs headline_insights honest). Mitigation:
  pick the honest spine; use the optimistic numbers only where they survive the ablation
  (the *environment quality* and *searched verifier* numbers do).

## Success criteria
- 16–18 slides, each with title + key point + timing; timings sum to 14–15.5 min.
- Every quantitative claim traces to a real number in `ARCHITECTURE.md` or
  `docs/headline_insights.md` (no invented figures).
- The ablation / honest-limitation is present and prominent, not hidden.
- `timing_check.py` parses the outline and confirms the budget; runs clean.
