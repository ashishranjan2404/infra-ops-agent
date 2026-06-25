# B2 — Summary: McNemar paired test over all condition pairs

## Task
The paper claims McNemar's paired significance test but never ran the full pairwise matrix.
B2 delivers a standalone `mcnemar.py` that ingests per-episode pass/fail from any pass@k
result JSON and emits a McNemar 2x2 table + exact p-value for every condition pair,
then runs it on the real cached results and reports real p-values.

## Deliverables (all under experiments/ralph_outputs/B2/artifacts/, no shared core edited)
- mcnemar.py — stdlib-only tool: binary thresholding (pass@k-consistent), aligned paired
  vectors, exact two-sided binomial p (math.comb), continuity-corrected chi2, all
  C(k,2)=10 condition pairs, per family (overall/simple/cascade/novel), Holm-Bonferroni
  multiple-comparison correction, pass rates, CLI.
- test_mcnemar.py — 11 stdlib unittest cases, all pass.
- mcnemar_pairwise_report.json — real output on A1 (glm-5p2) + A2 (deepseek-v4-pro).

## Real findings (Holm-corrected, alpha=0.05)
- REx is significant vs every control, both models (rex vs zero_shot/best_of_n/
  retry_realistic/rex_no_oracle: p_exact < 1e-6). Direction-clean: REx wins essentially
  every discordant pair (b10 = 0).
- Oracle ablation significant: rex vs rex_no_oracle p<1e-6 — the gain isn't only the oracle.
- Weak baselines mostly indistinguishable: best_of_n / retry_realistic / rex_no_oracle
  show no significant pairwise differences.
- Holm matters: best_of_n vs zero_shot on deepseek is raw-significant (p=0.013) but
  NOT significant after correction (p_holm=0.065) — exactly the over-claim the paper
  risked by not running the test.

## Validation
- 11/11 unit tests pass; py_compile clean.
- B2 independently reproduces A2's existing mcnemar discordant counts exactly (zero_shot
  100/99, best_of_n 88/88, retry_realistic 89/88, rex_no_oracle 91/91), generalizing A2's
  4-comparison block to the full 10-pair matrix with correction A2 lacked.

## Honest caveats (see 09_critique.md)
Seeds within an incident are correlated (independence assumption inflates n); novel-family
cells are underpowered (n_disc as low as 0-2); threshold sensitivity (0.8 cliff) not swept;
two models only. The big REx effects survive these; the marginal weak-baseline calls would not.

## Status: completed
