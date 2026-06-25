# B14 — Technical Spec

## Data structures (cost_model.py)
```python
@dataclass(frozen=True)
class Price:
    in_per_m: float      # USD / 1M input tokens
    out_per_m: float     # USD / 1M output tokens
    assumed: bool = False
    note: str = ""

@dataclass
class JobCost:
    model: str; condition: str
    proposer_calls: float
    input_tokens: int; output_tokens: int
    usd: float
    price_assumed: bool
    output_token_utilization: float
```

## Constants (all overridable)
- `PRICES: Dict[str, Price]` — Claude real; gateway/fireworks assumed.
- `DEFAULT_PRICE` — assumed fallback for unknown models.
- `N_BUDGET = 4`, `RETRY_EXPECTED_CALLS = 2.3`.
- `PROPOSER_CALLS = {zero_shot:1, best_of_n:4, retry_realistic:2.3, rex:4, rex_no_oracle:4}`.
- `OUTPUT_TOKENS_PER_CALL = 1400` (from `eval_pass_at_k.py` proposer max_tokens).
- `INPUT_TOKENS_PER_CALL = 1200` (assumed prompt size).
- `JUDGE_CALLS = 0` (deterministic P0 scorer; LLM-judge path documented at max_tokens=8).

## Function signatures
```python
def price_for(model: str) -> Price
def estimate_job_cost(model: str, condition: str, *,
                      output_token_utilization: float = 0.6) -> JobCost
```
- `usd = (in_tok/1e6)*in_per_m + (out_tok/1e6)*out_per_m`, summed over proposer (+judge if enabled).
- `in_tok = calls*INPUT_TOKENS_PER_CALL`; `out_tok = calls*OUTPUT_TOKENS_PER_CALL*util`.
- Unknown condition → `KeyError`. Unknown model → `DEFAULT_PRICE` (assumed).

## cost_per_dollar.py contract
- **Input:** result JSONs at the A1/A2 artifact paths. Schema relied on:
  `res["model"]`, `res["n_incidents"]` (or sum of `incidents_by_family`),
  `res["by_condition"][cond]["overall"]["pass@1"]`.
- **Per row:** `pass@1`, `usd_per_incident`, `usd_per_100_incidents`,
  `cost_mult_vs_zero_shot`, `pass@1_per_dollar = pass@1 / usd_per_incident`, `price_assumed`.
- **Output files:** `cost_efficiency.json` (metric, definition, sources, price_table,
  proposer_calls, rows) and `cost_efficiency_table.md` (main table + best-operating-point table).
- **Exit:** 0 on ≥1 row; 1 if no result JSON found.

## Test cases (test_cost_model.py)
1. Claude prices `assumed is False`; gateway slugs `assumed is True`.
2. Opus price == (5.0, 25.0).
3. `zero_shot`=1 call, `rex`/`best_of_n`/`rex_no_oracle`=N, `retry_realistic`∈[1,N].
4. rex cost / zero_shot cost ≈ N (same model).
5. opus zero_shot $ > glm zero_shot $.
6. utilization scales output cost only (input unchanged).
7. unknown condition → KeyError.
8. unknown model → assumed default, usd>0.
9. `JUDGE_CALLS == 0`.

## File formats
- JSON: indent=2, UTF-8. Markdown: GitHub pipe tables.
