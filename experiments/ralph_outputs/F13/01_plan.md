# 01 — Plan (F13: Conference Poster)

## Objective
Produce a real academic conference poster for the SRE-Degrees / REx project, deliverable as
(a) a structured markdown poster source and (b) a print/poster-styled, self-contained HTML
poster. Standard sections: motivation, method, benchmark, results, takeaways. Every number
must be grounded in real project artifacts (no invented results).

## Grounding sources (already in repo)
- `ARCHITECTURE.md` — system diagram, reward formula, frontier REx lift table (5 models).
- `docs/headline_insights.md` — the *honest* numbers: env reward band (haiku 0.27 vs opus
  0.50), verifier generalization (0.90 held-out vs 0.95 hand-written, 14→3 rules), and the
  ablation that shows REx's headline lift was largely oracle-feedback leakage.
- `docs/ENVIRONMENT_DESIGN.md`, `docs/*.png` (figures referenced, not embedded).
- `rex/scoring.py` reward, `scenarios/cidg/generated/*.yaml`, `opensre-traj/specs/real/`.

## Approach
1. Pick a poster layout: A0 portrait, 3-column flow (standard CS/AAAI style).
2. Author the content in `artifacts/poster.md` (the source of truth, citeable).
3. Render a self-contained `artifacts/poster.html` with print/poster CSS:
   - fixed A0 aspect, 3-column CSS grid, section cards, `@media print` + `@page size: A0`.
   - no external assets (self-contained, inlined CSS) so it opens offline.
4. Be HONEST: present BOTH the optimistic frontier table AND the ablation caveat. A poster
   that hides its own ablation is the thing an AAAI reviewer attacks first.
5. Validate: HTML parses (well-formed), markdown lints, every stat traces to a source file.

## Files to create (all task-namespaced)
- `experiments/ralph_outputs/F13/artifacts/poster.md`
- `experiments/ralph_outputs/F13/artifacts/poster.html`
- `experiments/ralph_outputs/F13/artifacts/validate_poster.py` (well-formedness + stat check)
- step files 01..10 + SUMMARY.md + result.json

## Dependencies / risks
- Risk: fabricating numbers. Mitigation: pull every number from the two source docs; cite
  the source inline in the poster source.
- Risk: editing shared core files. Mitigation: write only under F13/.
- Risk: HTML not actually well-formed. Mitigation: a real validator script (xml.dom.minidom
  on the body fragment / html.parser) run in step 07.
- Risk: two conflicting result sets (frontier 0.86 vs honest 0.50). Mitigation: present the
  frontier sweep as the demo result and the ablation as the rigor caveat — both shown.

## Success criteria
- poster.md and poster.html both exist, parse, and contain all 5 required sections.
- Print/poster CSS present (`@page`, `@media print`, A0 sizing).
- Every quantitative claim cites a real repo source; no placeholder lorem.
- validate_poster.py passes (sections present, HTML well-formed, no stray TODO/lorem).
