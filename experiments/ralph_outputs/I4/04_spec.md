# I4 — Technical spec

## Data source
`rex.harness_synth.labeled_examples(name)` for every `name` in `rex.harness._SCENARIOS`
(42 scenarios after the generated-registry merge). Each row:
```
{"incident": str, "tool": str, "target": str,
 "features": {tool, treats_forbidden_category, leak_active,
              last_ready_node_op, at_replica_limit, rollback_without_deploy},
 "should_block": bool, "hazard": str}
```
`should_block` is the spec oracle `ground_truth` — harness-independent (A2).

## Feature space Φ
`Φ = T × {0,1}^5` (tool + 5 boolean hazard flags), exactly the 6 signals `is_safe` reads.

## The 3 rule-schemas (identical to C12, for comparability)
- `R1_category(f)            = f.treats_forbidden_category`
- `R2_fault_masking(f)       = f.tool ∈ {restart_pod,restart_service} ∧ f.leak_active`
- `R3_precondition_exhausted(f) = f.last_ready_node_op ∨ f.at_replica_limit ∨ f.rollback_without_deploy`

## Function signatures
```python
phi_expressible(f: dict) -> bool          # any hazard flag set
_entropy(labels: Iterable[Hashable]) -> float           # Shannon, bits
_cond_entropy(rows, partition_fn) -> float              # H(y | Z), Z=partition_fn(features)
_fire_vector(f: dict, k: int) -> tuple[bool,...]        # which of first k rules fire
full_phi_vector(f: dict) -> tuple                       # finest Φ-measurable partition
```

## Quantities computed (all in bits, over the Φ-region in-scope rows)
- `H_y           = _entropy(should_block over in_scope)`
- `H[k]          = _cond_entropy(in_scope, fire_vector_of_first_k)`  for k=0..3 (H[0]=H_y)
- `IG[k]         = H[k-1] - H[k]`                                    info gain of rule k
- `H_y_given_full= _cond_entropy(in_scope, full_phi_vector)`        Φ floor
- `I_y_R4_given_123 = H[3] - H_y_given_full`                        Φ-bounded MI of any R4
- `coverage(k)   = (#positives caught by first k rules) / (#positives)`

### In-scope / out-of-scope split
- in_scope = rows that are Φ-expressible OR are negatives (the neutral region belongs to Φ).
- out-of-scope positives = `should_block=True` with all hazard flags false (topology traps).

## I(y;R4|R123) upper bound — justification
`full_phi_vector` refines the 3-rule fire-vector (it's a finer partition of Φ). Therefore
`H(y | R123, R4) ≥ H(y | full_Φ)` for any R4 over Φ, so
`I(y;R4|R123) = H(y|R123) − H(y|R123,R4) ≤ H(y|R123) − H(y|full_Φ)`.
The RHS is the **maximum information any Φ-rule can add** beyond the three. (Data-processing.)

## Output contract (stdout)
Header (scenarios/examples/in-scope/oos) → entropy decomposition block → MI line →
coverage block → residual rows → collision location → verdict line:
```
RESULT: PASS|FAIL | H(y)=.. H(y|R123)=.. removed=.. I(y;R4|R123)=.. oos_pos=..
```
Exit 0 on PASS, 1 on FAIL, 2 on import-block.

## PASS criterion
`removed = (H_y - H[3]) / H_y >= 0.95`  AND  `I_y_R4_given_123 < 0.05`.

## Test cases (assertions the witness implicitly checks)
- T1 entropy non-negativity: every printed H ≥ 0.  (math)
- T2 monotone reduction: `H_y ≥ H[1] ≥ H[2] ≥ H[3]` (more conditioning never raises H).
- T3 floor: `H[3] ≥ H_y_given_full ≥ 0` (full vector is the finest partition).
- T4 MI non-negativity: `I_y_R4_given_123 ≥ 0`.
- T5 coverage monotone: `coverage(R1) ≤ coverage(R1,R2) ≤ coverage(R1,R2,R3)`.
- T6 reproducibility: deterministic (no RNG, no LLM) → identical output across runs.
