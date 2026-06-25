# 02 — Grill (5 personas, 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**AAAI** (AAAI Reviewer), **RLE** (RL Engineer), **DEVO** (DevOps Lead).

## Round 1 — initial takes
- **SMR:** Supplementary material exists to make results reproducible. A static
  hand-written table is worthless; it must be generated from the same artifacts the
  experiments consume, so the catalog is provably the eval substrate.
- **PSRE:** As an operator I want the *root cause* and the *canonical fix* per
  incident, and whether it cascades. Without the fix column this is just a list of
  names. Include the fix ordering note — order matters in real remediation.
- **AAAI:** Reviewers want provenance. Each synthetic incident claims to be grounded
  in a real outage — show the `source` (and URLs if any) so we can audit grounding.
  If 40/51 are "Synthetic simple incident", that's a finding the paper must own.
- **RLE:** The catalog should expose the fields the harness/judge actually keys on
  (root_cause.location, canonical_fix.steps) so reward grounding is traceable.
- **DEVO:** Make it regenerable in CI. One command, deterministic output, exit codes.
  Emit JSON too so a diff gate can catch silent spec changes.

## Round 2 — forced disagreement (react to a named persona)
- **PSRE → AAAI:** I disagree with leading on provenance. Half these specs are
  *synthetic* by construction (failure-class generators). Demanding a real URL for
  every row would force us to fabricate citations — worse than honestly labeling
  them "Synthetic". Show source verbatim; don't dress it up.
- **AAAI → PSRE:** Pushing back. "Show it verbatim" is fine, but then the *summary*
  must surface that 40/51 cascade and 40/51 hide the root cause — otherwise a reader
  skims the table and over-claims realism. The honesty has to be in aggregate stats,
  not buried in 51 rows.
- **RLE → SMR:** You said "generate from the artifacts the experiments consume" — but
  the experiments consume these via `sim/engine.py` loading, not the raw YAML keys I
  list. I disagree that listing raw keys is enough; we should at least note topology
  size and cascade flag so the catalog reflects *difficulty*, not just identity.
- **DEVO → RLE:** You want more derived fields; I want a stable schema. Every extra
  computed column is a thing that can throw on a sparse spec. Keep extraction
  defensive and additive — never crash the whole run because one spec lacks
  `assertions`.
- **SMR → DEVO:** Deterministic JSON is good, but don't over-index on CI. The
  primary deliverable is human-readable supplementary material for the paper; the
  JSON is a secondary convenience. Don't let the diff-gate tail wag the dog.

## Round 3 — synthesis
Consensus reached:
1. Generate from YAML ground truth (SMR, all).
2. Columns: id, title, root cause (with hidden flag), canonical fix (ordered),
   source (PSRE + AAAI).
3. Add an aggregate **Summary** section surfacing cascade count, hidden-root-cause
   count, and failure-class distribution — this carries the honesty AAAI demanded
   without fabricating citations PSRE warned against.
4. Defensive `.get()` extraction so one malformed spec never kills the run (DEVO).
5. Emit both MD (primary) and JSON (secondary, for diff gate) (DEVO/SMR balance).
6. Include topology size + cascade flag per incident to reflect difficulty (RLE).
