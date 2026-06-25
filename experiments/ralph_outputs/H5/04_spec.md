# H5 — 04 Spec

## Manifest schema: `sre-degrees.promotion-manifest/v1`
```jsonc
{
  "schema": "sre-degrees.promotion-manifest/v1",
  "generated_at": "<ISO-8601 UTC, seconds>",
  "gate": {
    "promote_p1": 0.80,            // float [0,1]: min absolute pass@1
    "promote_ci_lo": 0.70,         // float [0,1]: min 95% CI lower bound
    "min_lift_over_baseline": 0.20 // float [0,1]: min pass@1 lift vs same-model zero_shot
  },
  "families": ["simple","cascade","novel"],
  "sources": { "A1": "<provenance>", "A2": "<provenance>" },
  "candidates": [ <Candidate>, ... ]
}
```

### Candidate object
```jsonc
{
  "id": "<model>/<condition>",          // unique
  "model": "glm-5p2" | "deepseek-v4-pro",
  "condition": "zero_shot|best_of_n|retry_realistic|rex|rex_no_oracle",
  "source": "A1" | "A2",
  "n": int, "passes": int,
  "pass_at_1": float, "ci_lo": float, "ci_hi": float,
  "pass_at_2": float|null, "pass_at_5": float|null,
  "lift_over_baseline": float,          // pass_at_1 - zero_shot(same model).pass_at_1
  "by_family": { "<fam>": {"n":int,"pass_at_1":float,"ci_lo":float,"ci_hi":float}, ... },
  "decision": "PROMOTE" | "HOLD" | "REJECT",
  "reasons": [ "pass@1 0.90 >= 0.80", "CI_lo 0.83 >= 0.70", "lift 0.67 >= 0.20" ]
}
```

## Function signatures (gen_manifest.py)
- `decide(p1: float, ci_lo: float, lift: float) -> (str, list[str])`
  - returns `PROMOTE` iff `p1>=promote_p1 AND ci_lo>=promote_ci_lo AND lift>=min_lift`;
    `REJECT` iff `lift<min_lift`; else `HOLD`.
- `load_a1() -> list[Candidate]` — reads `summary_table.json` (keys `p1`, `ci`, `p2`, `p5`).
- `load_a2() -> list[Candidate]` — reads `ablation_pass_at_k_*.json` `by_condition`
  (keys `pass@1`, `ci95`, `pass@2`, `pass@5`).
- `main()` — concatenate, stamp schema + provenance, write `sample_manifest.json`.

## HTML contract
- `validate(m)` throws unless `m.schema === "sre-degrees.promotion-manifest/v1"`,
  `Array.isArray(m.candidates)`, and `m.gate` present.
- `fetchSample()` → `fetch("sample_manifest.json")`; on non-OK or network error, show the
  loud error box with serve hint.
- File `<input type=file>` → `FileReader` → `loadManifest(JSON.parse, name)`.
- `render()` groups candidates by model, renders sortable table; pass@1 cell draws a bar
  (width=pass@1), a CI band (`ci_lo..ci_hi`), and a yellow tick at `gate.promote_p1`.

## Test cases
1. `python3 gen_manifest.py` exits 0; prints PROMOTE/HOLD/REJECT counts.
2. `sample_manifest.json` is valid JSON with `schema==v1` and 10 candidates.
3. Only conditions clearing all three tests are PROMOTE (expect the two `rex` rows).
4. HTML parses (HTMLParser, no exception) and contains the schema string + fetch logic.
5. Served over HTTP: `GET dashboard.html` and `GET sample_manifest.json` both 200.
6. Node DOM-shim run of the page script over the real manifest yields counters
   `tot=10, prom=2, hold=0, rej=8` with no JS error and `err` hidden.
