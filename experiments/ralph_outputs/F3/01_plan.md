# F3 — Plan: Write the Conclusion ("graduation not deployment")

## Objective
Write a strong, publication-grade **Conclusion** section (markdown) for the SRE-Degrees
project that frames the incident-response agent as **earning autonomy through graduated
evaluation** — a *graduation*, not a *deployment*. The metaphor must be load-bearing, not
decorative: it has to map cleanly onto machinery that already exists in the repo.

## Why this framing is correct (grounding in the repo's thesis)
The project is literally named **SRE-Degrees**. The graduation metaphor is already encoded:

- **Trust tiers as a transcript.** `tools_registry.json` assigns every tool a tier:
  `autonomous` / `approval` / `blocked`. The README (`README.md:77-79`) states the design
  *promotes* a tool `human-approval → autonomous` (or demotes it) "based on proven
  consistency … **like a junior engineer earning trust**." That is graduation, made
  mechanical.
- **Escalation is a passing grade, not a failure.** `ARCHITECTURE.md` shows the 0.86 REx
  ceiling is `(4×1.0 + 0.30)/5` — every model solves the 4 solvable incidents **and
  correctly escalates the 1 unsolvable one** (`singleton_node_notready`, no safe fix). A
  graduate who knows the limit of their competence and hands off is *more* trustworthy, not
  less. The "safety gate holds."
- **A root-cause-aware reward is an exam that can't be crammed.** The reward
  (`0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap`) means "the metric came back up"
  is worth only 45%; tripping the trap zeroes you. You cannot *deploy* your way past this —
  you must *demonstrate understanding of the mechanism*. That is the difference between
  shipping a binary and conferring a degree.
- **The curriculum is a degree program.** `rex/curriculum.py` runs simple→hard: 15 generated
  single-leaf incidents (loud alert = cause) then 5 reconstructed real cascades (loud alert
  is a downstream victim). You don't graduate on the easy tier; you graduate by holding up on
  the cascades that mislead frontier models on the first try.

## Approach
1. Read the canonical thesis docs (`ARCHITECTURE.md`, `README.md`, `docs/headline_insights.md`)
   to pull the *exact* numbers and mechanisms so the Conclusion is grounded, not invented.
2. Draft a Conclusion with this skeleton:
   - **The shift in stance**: deployment (one-time pass/fail, then trust by default) vs
     graduation (continuous, tiered, revocable, mechanism-aware).
   - **What we built that makes graduation real** (4 mechanisms above, each tied to a file).
   - **Evidence it works** (REx lift table, the 0.86-is-the-ceiling-not-saturation argument,
     escalation as the signature of a graduate).
   - **What a degree from this program certifies** (and explicitly what it does *not*).
   - **Limits / future cohorts** (honest: revocation isn't yet automated; cohort is small).
3. Validate: markdown parses, all cited numbers match the source docs, no placeholder text.

## Files to create
- `artifacts/CONCLUSION.md` — the deliverable (the Conclusion section).
- `artifacts/claims_provenance.tsv` — every quantitative claim → source file:line (audit).
- `artifacts/validate_conclusion.py` — checker: markdown structure + provenance numbers
  actually appear in the cited source files.

## Files to modify
None. This is a pure-authoring task. No shared core file is touched (brief rule).

## Dependencies
- Source docs already in repo (read-only). Python 3.13 stdlib only for the validator.

## Risks
- **Risk: metaphor outruns the machinery** (purple prose ungrounded in code). Mitigation:
  every paragraph cites a concrete file/mechanism; the validator fails if a cited number is
  not literally present in its source doc.
- **Risk: overclaiming graduation = real-world safety.** Mitigation: an explicit "what this
  degree does NOT certify" subsection.
- **Risk: numbers drift from the canonical docs.** Mitigation: `claims_provenance.tsv` + the
  validator pin every figure to a source line.

## Success criteria
1. `CONCLUSION.md` is a real, self-contained, well-structured Conclusion (≥ ~700 words),
   not a stub.
2. The "graduation not deployment" framing is explicit, sustained, and *mechanically*
   grounded in ≥4 named repo artifacts.
3. Every quantitative claim traces to a source line via `claims_provenance.tsv`.
4. `validate_conclusion.py` passes (structure + provenance checks).
