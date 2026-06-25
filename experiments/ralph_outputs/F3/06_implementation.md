# F3 — Implementation

## What I built
A grounded, validated **Conclusion** section plus two thin guard artifacts. No shared core
file was edited (brief rule honored — this is a pure-authoring task).

### Artifacts (all under `experiments/ralph_outputs/F3/artifacts/`)
1. **`CONCLUSION.md`** — the deliverable. 929 words. Sustains the "graduation, not
   deployment" framing across five subsections:
   - *Graduation, not deployment* — defines both terms; disarms the CI/CD misreading.
   - *What makes graduation real* — four mechanisms, each tied to a named repo artifact:
     trust tiers (`tools_registry.json`), the uncrammable reward (`rex/scoring.py`), the
     curriculum-as-degree-program (`rex/curriculum.py`), escalation-as-passing
     (`singleton_node_notready`, the 0.86 ceiling).
   - *The evidence* — leads with behavior (escalation; haiku+REx 0.68 > opus zero-shot 0.42;
     spread 0.63–0.81 compressing to a uniform 0.86), then the argued ceiling
     `(4×1.0 + 0.30)/5`, with the reward math in support.
   - *What this degree certifies — and what it does not* — explicit limits: n is small, the
     diagnosis grade is an LLM-judge, sim ≠ cluster, and the demotion arrow is **designed and
     partially exercised but not yet automated**.
   - *Future cohorts* — automate demotion, widen the curriculum, independent oracle, live
     cluster.
2. **`claims_provenance.tsv`** — 9 quantitative claims, each pinned to a `file:line` with the
   exact (Unicode-faithful) value string copied from the source doc.
3. **`validate_conclusion.py`** — stdlib-only checker: ordered/disjoint structure regexes,
   content contract (word floor, framing phrase, ≥4 named artifacts, reward coefficients,
   ceiling-identity tokens, revocation-honesty clause, no placeholders), and a provenance
   drift check (every cited value still present in its source file).

## Design decisions carried from the grill / ouroboros
- Behavior-first evidence ordering (AAAI/RLE in `02`); formula supports, doesn't lead.
- Explicit "does NOT certify" paragraph with the *non-automated demotion* admission stated
  aloud (SMR/PSRE concession in `02`, accepted in `03`).
- Provenance value strings are EXACT source substrings including Unicode `×`/`·`/`−`
  (Engineer-1 fix in `05`), so the check is a true drift detector.
- Structure regexes made disjoint and order-checked by sequential post-offset scan
  (Engineer-2 fix in `05`) to remove `## What...` cross-match ambiguity.
- Prose is the primary deliverable; validator/TSV kept thin (Engineer-3 fix in `05`).

## Source grounding (read-only)
`ARCHITECTURE.md` (thesis, reward, REx table, 0.86 ceiling, curriculum numbers), `README.md`
(trust tiers, "junior engineer earning trust"). One provenance line was corrected during
testing: the reward formula lives at `ARCHITECTURE.md:75`, not README (caught by the
validator — see `07`).
