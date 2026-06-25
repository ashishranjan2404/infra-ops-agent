# F14 — SUMMARY

## Task
Prepare a real 15-minute talk outline (AAAI-style) for the SRE-Degrees project: slide-by-slide
(title + key point + timing), grounded in the actual narrative and results.

## Deliverables
- **artifacts/talk_outline_15min.md** — 17-slide, 15:00 outline with per-slide key points,
  speaker notes, and a 5-item Q&A backup appendix. 13 [ARCH] + 9 [HEAD] source tags; every
  headline number traces to ARCHITECTURE.md or docs/headline_insights.md.
- **artifacts/timing_check.py** — stdlib validator (passing self-test) that enforces contiguous
  numbering, no slide > 75s, and total == 15:00. Runs clean, exit 0.

## Narrative spine (chosen for AAAI credibility)
Thesis = the verifiable incident-response environment. Headline result = the searched safety
verifier (14->3 rules, 0.90 held-out vs 0.95 hand-written). REx's refinement lift is adjudicated
by an ablation slide (REx 0.25 ~= zero-shot 0.24 once the oracle hint is stripped) rather than
oversold — the 0.86 table lives only in backup B2. This honest framing was driven by the grill
(5 personas) and ouroboros self-critique.

## Validation
python3 .../timing_check.py -> self-test passes, 17 slides, total=15:00, PASS, exit 0. The
validator caught and forced a fix of a real 13:45-vs-15:00 budget error in the first draft.

## Honest limitations
It's an outline, not a rendered deck; timing is budgeted not rehearsed; the verifier's held-out
n=3 remains the soft underbelly (scoped, not solved). See 09_critique.md.

## Shared-core safety
No shared core files edited. ARCHITECTURE.md / docs/headline_insights.md read-only. All writes
under experiments/ralph_outputs/F14/.
