# 06 — Implementation

## What I built (all under experiments/ralph_outputs/F13/artifacts/)
1. **`poster.md`** (6.4 KB) — markdown source of the A0 academic poster. Source of truth.
   Contains every required section (Motivation, Method, Benchmark, Results, Takeaways) plus
   The Cascade, Environment (hero), Two-Tier Contract, and Reproduce. Every quantitative claim
   carries an inline `[src: <file>]` tag.
2. **`poster.html`** (12 KB) — self-contained, print/poster-styled A0 portrait poster.
   - A0 portrait container (841mm × 1189mm), 3-column CSS grid.
   - 10 `<section class="card">` panels; the Environment panel is the `.hero`; the ablation
     panel is the `.rigor` panel (same heading size/card style as the frontier panel — equal
     visual weight, tagged "⚠ rigor check"), per the ouroboros fix.
   - Frontier sweep rendered as a real `<table>`.
   - Print CSS: `@page { size:A0 portrait; margin:0 }`, `@media print { ... }`,
     `body{margin:0}`. System font stack only; fully inlined CSS; no external assets → opens
     offline.
3. **`validate_poster.py`** — stdlib-only validator (HTMLParser tag-stack with void-element
   handling, required-section check, print-CSS check, placeholder scan, and a tolerant
   `[src:]` repo-path existence check).

## Grounding (no invented numbers)
Every number traces to a real repo file:
- Reward formula, frontier sweep, within-group spread, scenario catalog, two-tier contract →
  `ARCHITECTURE.md`.
- Honest one-shot band (haiku 0.27 / opus 0.50), verifier generalization (0.90 vs 0.95,
  14→3 rules), ablation (REx 0.25 ≈ zero-shot 0.24) → `docs/headline_insights.md`.
The validator confirms all 9 cited repo file-paths exist on disk.

## Shared-core safety
No shared core file was edited. All writes are under
`experiments/ralph_outputs/F13/`. The poster references `rex/*`, `sim/*`, `agent/*`, `docs/*`
by path for citation only — none are modified.

## Design decisions carried from the grill / ouroboros
- Ablation shown at equal weight to the frontier table (REV + Engineer B).
- 0.86 described as the *designed* safe ceiling, not a measured decomposition (Engineer B).
- Two-tier contract box distinguishing reproducible sim from mechanism-validated GKE (PSRE).
- No false "300dpi/CMYK" claim — footer states raster/CMYK is a downstream step (Engineer C).
