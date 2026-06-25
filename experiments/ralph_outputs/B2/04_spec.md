# B2 — Step 4: Technical Spec

## Input file format (pass@k result JSON; fields used)
```jsonc
{
  "model": "<str>", "label": "<str|null>",
  "threshold": 0.8,            // reward >= threshold => PASS
  "seeds": 3,
  "incidents_by_family": {"simple":[...],"cascade":[...],"novel":[...]},
  "by_condition": {
    "<cond>": { "per_incident_rewards": { "<incident>": [r0, r1, ...] } }
  }
}
```
Conditions in the real data: `zero_shot, best_of_n, retry_realistic, rex, rex_no_oracle`.
Pairing key: an episode is identified by (incident, seed_index); the same key exists in
every condition, so conditions are paired sample-for-sample.

## Function signatures (artifacts/mcnemar.py)
```python
def to_binary(reward: float, threshold: float) -> int
    # 1 if reward >= threshold else 0

def mcnemar_table(a_bits: list[int], b_bits: list[int]) -> dict
    # -> {n_pairs, both_pass, both_fail,
    #     a_pass_b_fail(b01), a_fail_b_pass(b10), n_discordant,
    #     p_exact, chi2_cc}
    # p_exact = min(1, 2 * sum_{i=0..min(b01,b10)} C(n,i) * 0.5**n); 1.0 if n==0
    # chi2_cc = (|b01-b10|-1)^2 / n_disc   (continuity corrected; 0 if n==0)
    # raises ValueError on length mismatch

def holm_bonferroni(pairs: list[tuple[str,float]], alpha: float) -> dict
    # step-down Holm: rank-r p compared to alpha/(m-r); monotone-enforced p_holm
    # -> {label: {p_raw, p_holm, significant_holm}}

def aligned_bits(data, cond, incidents, threshold) -> list[int]
    # incident-major, seed-order-preserved flatten; raises KeyError on missing incident

def family_incidents(data) -> dict[str,list[str]]
    # {"overall": all incidents} + per-family lists (sorted, deterministic)

def analyze_file(data, threshold_override, alpha) -> dict
    # per family: C(k,2) pair tables + Holm flags; plus significant_raw per pair

def main(argv) -> int   # CLI; exit 0 ok, 2 on usage/data error
```

## Output report format
```jsonc
{
  "alpha": 0.05,
  "files": {
    "<path>": {
      "model","label","threshold","seeds","conditions","n_condition_pairs","alpha",
      "by_family": {
        "<fam>": {
          "n_incidents","n_pairs_per_test",
          "pairs": {
            "<condA>__vs__<condB>": {
              "n_pairs","both_pass","both_fail","a_pass_b_fail","a_fail_b_pass",
              "n_discordant","p_exact","chi2_cc","pass_rate_a","pass_rate_b",
              "p_raw","p_holm","significant_holm","significant_raw"
            }
          }
        }
      }
    }
  }
}
```

## CLI
```
python3 mcnemar.py RESULT.json [RESULT2 ...] [--out OUT.json] [--alpha 0.05] [--threshold T]
```

## Test cases (test_mcnemar.py, stdlib unittest)
- `to_binary`: boundary at threshold (0.8->pass, 0.79->fail).
- `mcnemar_table`: known b01/b10/both counts; n_disc=0 -> p=1.0, chi2=0;
  exact binomial (b01=9,b10=1) matches hand `2*(C10,0+C10,1)/2^10`; symmetry swaps cells,
  p direction-agnostic; length mismatch raises.
- `holm_bonferroni`: monotone non-decreasing; (0.001,0.04,0.6) => only first significant;
  all-tiny => all significant.
- `aligned_bits`: order == [inc1seed0, inc1seed1, inc2seed0, ...]; missing incident raises.
- end-to-end: synthetic 2-cond file where A dominates B -> b01=3,b10=0, n_condition_pairs=1.

## API contract / invariants
- Pairing requires equal-length vectors -> enforced (ValueError).
- p_exact in [0,1]; n==0 -> 1.0 (no evidence).
- Significance flags are reporting-only; never affect exit code.
- Deterministic: no RNG, sorted incident/condition iteration.
