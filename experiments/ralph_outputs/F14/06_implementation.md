# F14 — 06 Implementation

## What I built
1. **`artifacts/talk_outline_15min.md`** — the deliverable. A 17-slide, 15:00 talk outline for
   SRE-Degrees, slide-by-slide with title + key point + per-slide timing + a speaker note each,
   plus a 5-item backup-slides appendix for Q&A. Every quantitative claim carries a `[ARCH]` or
   `[HEAD]` source tag pointing at the repo's two narrative documents.

2. **`artifacts/timing_check.py`** — a stdlib-only validator that parses the outline's slide
   headings, checks contiguous numbering, flags any slide > 75s, and confirms the total equals
   the 15:00 target. Has an inline self-test (8 assertions) that runs before validating the file.

## Grounding (no invented numbers)
All figures were lifted from:
- `ARCHITECTURE.md`: reward function `0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap`, the
  "resolved = 45%" point, the trap (scale crash-looping control plane → herd datastore),
  two-tier reality contract, curriculum hard-tier floor ~0.19–0.42, one-command reproduce.
- `docs/headline_insights.md`: env band 20–50% with variance (haiku 0.27 vs opus 0.50);
  searched verifier 0.90 held-out vs 0.95 hand-written, 14→3 rule compression, 7/3 split;
  the ablation (REx 0.25 ≈ zero-shot 0.24 once oracle hint stripped, best-of-N 0.24, retry
  0.23); open-model training status (Qwen3-8B/30B, easy ~0.5, hard headroom ~0.35).

## Key design decision (from the grill + ouroboros)
The two source docs are in tension: `ARCHITECTURE.md` presents a triumphant "REx lifts every
model to 0.86" table, while `headline_insights.md` shows that lift is largely oracle-feedback
leakage. The talk resolves this honestly: REx is introduced neutrally (slide 9), its lift is
*adjudicated by an ablation slide* (slide 12), and the rosy 0.86 table is demoted to backup
B2 "with the ablation caveat." The thesis is the **verifiable environment**; the headline
result is the **searched safety verifier**. This is the defensible, reviewer-proof framing.

## Shared-core safety
No shared core files were edited. All artifacts live under
`experiments/ralph_outputs/F14/`. `ARCHITECTURE.md` and `docs/headline_insights.md` were read
only. No proposed core-file change was needed for this task (it is a content deliverable), so
no `.patch` was produced.

## How to run / verify
```
python3 experiments/ralph_outputs/F14/artifacts/timing_check.py
# -> [selftest] all assertions passed ; ... ; total=15:00 target=15:00 ; PASS ; exit 0
```
