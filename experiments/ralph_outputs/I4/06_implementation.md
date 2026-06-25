# I4 — Implementation

## Artifacts built (real, runnable, task-namespaced)
1. `artifacts/entropy_witness.py` — the runnable measurement. Imports ONLY pure-data
   helpers (`rex.harness._SCENARIOS`, `rex.harness_synth.labeled_examples`) — no
   `agent.llm` / LLM path. Computes, over all 42 scenarios:
   - `H(y)` and `H(y|R1..Rk)` via `_entropy` / `_cond_entropy` (Shannon, bits);
   - per-rule information gain `IG(Rk)`;
   - `I(y;R4|R123)` as the Φ-bounded ceiling `H(y|R123) − H(y|full_Φ)` (data-processing);
   - coverage of the should-block mass by the first k rules;
   - the in-Φ / out-of-Φ split, residual rows, and the collision location.
   Self-checking PASS criterion: `≥95% of H(y) removed` AND `I(y;R4|R123) < 0.05 bits`.
2. `artifacts/three_rules_information_argument.md` — the argument, every number grounded in
   the witness output, composed with C12's Lemma 1, with an explicit argument-vs-proof table.

## Key implementation decisions
- **Reused C12's 3 rule-schemas verbatim** so the two artifacts are directly comparable;
  this is "build on C12", not "duplicate" — C12 measures *accuracy*, I4 measures *bits*.
- **Φ split**: in-scope = Φ-expressible positives + all negatives; out-of-scope = the 35
  topology-trap positives whose flags are all false. Reported separately (ouroboros α).
- **MI as a ceiling via the full feature vector**: the finest Φ partition refines the 3-rule
  fire-vector, so `H(y|R123)−H(y|full_Φ)` upper-bounds any R4's gain (ouroboros β; framed as
  a ceiling, not an exact value, in the doc).
- **No shared core file touched.** The witness imports `rex/*` read-only.

## Proposed change to shared core (NOT applied — documented per brief)
None required. The argument is *about* `rex/harness.py:is_safe` and `rex/harness_synth.py`
as they stand; it neither needs nor proposes a code change. If one wanted to *close* the
0.0344-bit residual (§6a), the change would be a **7th feature**
`rollback_targets_bad_content` added to `harness_synth.features` — but that is a feature
addition, explicitly out of scope here, and is left as a documented recommendation, not a patch.

## Measured headline (real output)
```
H(y)=0.9710  H(y|R1)=0.1284 (IG 0.8426)  H(y|R1,R2,R3)=0.0433 (95.5% of H(y) removed)
H(y|full Φ)=0.0089   I(y;R4|R123) ≤ 0.0344 bits
coverage(R1)=0.9495  coverage(R123)=0.9908   out-of-scope positives=35
RESULT: PASS
```
