# B4 — Technical Spec

## Inputs (read-only)
- `scenarios/cidg/generated/*.yaml` (51 files)
- `scenarios/cidg/generated/registry.json` (32 labelled: family ∈ {simple,cascade,novel})
- `experiments/ralph_outputs/A8/artifacts/heldout_split.csv` (cidg_key, family, held_out, ...)
- `experiments/ralph_outputs/A7/artifacts/difficulty_scores.csv` (id, difficulty_bucket)
- Result JSONs (pre-computed pass@k):
  - `experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json`
  - `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json`
  - (auto-discovered glob; `.partial` reported separately)

## Artifact 1 — classify_incidents.py

### Data structures
```python
TYPES = ("simple", "cascade", "novel")

@dataclass
class IncidentType:
    file: str            # basename of yaml
    incident_id: str     # meta.id or registry key
    type: str            # one of TYPES
    source_tier: str     # "registry" | "a8" | "name-rule" | "real-outage" | "mechanics"
    difficulty: str|None # easy|medium|hard from A7, or None
```

### Functions
```python
def load_registry(path) -> dict[str,str]          # cidg_key -> family
def load_a8_families(csv_path) -> dict[str,str]    # cidg_key -> family
def load_a7_difficulty(csv_path) -> dict[str,str]  # incident_id -> bucket
def yaml_id(doc) -> str                            # doc['meta']['id']
def is_real_outage(doc) -> bool                    # meta.source matches  <Company> <YYYY>
def n_slo_nodes(doc) -> int                        # len({s['node'] for s in doc['slo']})
def classify_one(fname, doc, reg, a8, a7) -> IncidentType   # ordering rule from 03
def main() -> None                                 # writes csv + json, prints counts
```

### Classification ordering (must match 03_improved_plan)
1. registry/A8 family if present (key = snake_case of id)
2. filename `-leaf-` → simple ; `-cascade-` → cascade
3. `is_real_outage(doc)` → novel
4. `assertions.cascades==True and n_slo_nodes>1` → cascade
5. else simple

`is_real_outage`: regex `\b(19|20)\d\d\b` in `meta.source` AND source not starting with
"Synthetic". The 80-89 series all have dated real sources.

### Outputs
- `incident_types.csv`: file,incident_id,type,source_tier,difficulty
- `incident_types.json`: {schema, count, by_type:{counts}, incidents:[IncidentType...]}

### Test assertions (T-series in 07)
- T1: 51 yaml files in → 51 rows out (every file labelled, no dupes).
- T2: every type ∈ TYPES.
- T3: for the 32 registry incidents, classifier type == registry family (tier=registry/a8).
- T4: counts cross-check — registry says simple=8,cascade=14,novel=10 for the 32 subset.
- T5: a11 `-leaf-` files → simple (3 of them), `-cascade-` → cascade (3 of them).
- T6: each 80-89 real-outage file gets a non-null type and tier ∈ {real-outage,mechanics,name-rule}.

## Artifact 2 — stratify_pass_at_k.py

### Functions
```python
def discover_results() -> list[Path]               # glob result JSONs, split headline vs partial
def load_result(path) -> dict
def family_block(result, condition, ftype) -> dict|None  # by_condition[c].by_family[ftype]
def render_type_table(ftype, results) -> str       # one Markdown table across models x conditions
def check_consistency(result, classifier_json) -> list[str]  # incidents_by_family vs our labels
def main() -> None
```

### Table format (one .md per type)
```
# pass@k — type: cascade

| model | condition | n | passes | pass@1 (CI95) | pass@2 | pass@5 | mean_r | std |
|-------|-----------|---|--------|---------------|--------|--------|--------|-----|
| glm-5p2 | zero_shot | .. | .. | 0.21 [0.10,0.38] | .. | .. | .. | .. |
| glm-5p2 | rex       | .. | .. | ...
| deepseek-v4-pro | zero_shot | ...
```
Footer: classified-but-unevaluated incidents of this type; provisional `.partial` note.

### Outputs
- `stratified_simple.md`, `stratified_cascade.md`, `stratified_novel.md`
- `stratified_pass_at_k.json`: {types, results_used, partial_results, tables:{type:[rows]},
  consistency_mismatches:[...]}

### Tests (07)
- T7: 3 md files produced, each has a header for its type and ≥1 data row.
- T8: numbers in B4 tables == A1 result's by_family numbers (parity check, exact).
- T9: consistency check runs; mismatches list is empty OR explicitly reported.
