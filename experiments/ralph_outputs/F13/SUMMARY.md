# F13 — Conference Poster — SUMMARY

## Task
Create a real academic conference poster for the SRE-Degrees / REx project, with the standard
sections (motivation, method, benchmark, results, takeaways), grounded in real results, and
print/poster-styled if delivered as HTML. Do not edit shared core files.

## Delivered (all under experiments/ralph_outputs/F13/artifacts/)
- poster.md — markdown poster source (source of truth, every claim [src:]-cited).
- poster.html — self-contained A0 portrait, 3-column, print-styled poster
  (@page size:A0 portrait, @media print, inlined CSS, system fonts -> opens offline).
  10 section cards incl. hero (Environment) and a co-equal .rigor ablation panel.
- validate_poster.py — stdlib validator (well-formedness + required sections + print CSS +
  no-placeholder + cited-source existence). Passes, exit 0.

## Grounding (real, no invented numbers)
- Reward 0.30*diag + 0.25*fix + 0.45*resolved - 0.60*trap, frontier sweep (5 models ->
  0.86 designed ceiling), within-group spread 0.0/0.15/1.0 <- ARCHITECTURE.md.
- Honest one-shot band (haiku 0.27 / opus 0.50), verifier generalization (0.90 vs 0.95,
  14->3 rules), ablation (REx 0.25 ~ zero-shot 0.24) <- docs/headline_insights.md.
- Validator confirms all 9 cited repo file-paths exist.

## Key design choice (honesty)
Frontier lift table and the ablation caveat are shown at equal visual weight — the poster
does not bury its own ablation. 0.86 is labeled the designed safe ceiling; two-tier contract
(sim reproducible / GKE mechanism-validated) is stated.

## Status: completed
Validator passes; outputs are real and grounded. Not yet a final board-ready poster (needs a
browser PDF render, embedded figures, author metadata) — documented in 09_critique.md.

## Shared-core safety: clean
No shared core file edited; all writes under experiments/ralph_outputs/F13/.
