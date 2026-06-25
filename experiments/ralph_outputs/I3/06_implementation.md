# I3 — Implementation

## Artifacts built (all under experiments/ralph_outputs/I3/artifacts/)
- **`dip_test.py`** — `dip_test(samples) -> (D, p)`. Primary engine: the vetted
  `diptest` v0.11 package (Python binding to Hartigan & Hartigan's AS 217 `diptst`
  C routine + the original analytic p-value interpolation table). A pure-NumPy
  GCM/LCM fallback statistic is included but explicitly labelled untrusted (it is
  only correct in the uniform/strongly-bimodal regimes; the package is used for
  the real analysis — `_HAVE_PKG=True` in run.log).
- **`run_dip_on_rewards.py`** — loads REAL committed reward data and runs the test:
  - A1 `full_pass_at_k_glm-5p2.json` (5 conditions x 126 episodes),
  - A2 `ablation_pass_at_k_deepseek-v4-pro.json` (5 x 150),
  - `rex/runs/diagnostic_probe_*.jsonl` (per-iteration `score`, n=12).
  Emits `dip_results.json` + a console table. For each distribution it reports D,
  p, conclusion at alpha=0.05, and pole masses (frac at <=0.1 / >=0.9 / middle).
- **`test_dip_test.py`** — validation suite (Gaussian gate, bimodal gate, range,
  determinism). 6/6 pass.
- **`make_figure.py` + `reward_dip_histograms.png`** — A1 reward histograms with
  D/p/verdict annotations.
- **`dip_results.json`**, **`run.log`** — outputs.

## Dependency installed
`python3 -m pip install diptest` (v0.11). No shared core file was modified; no
live cluster / API used — runs fully offline in ~1s.

## Headline numbers (alpha=0.05)
| distribution (A1/glm-5p2) | n | D | p | verdict |
|---|---|---|---|---|
| zero_shot | 126 | 0.143 | <1e-4 | BIMODAL |
| best_of_n | 126 | 0.151 | <1e-4 | BIMODAL |
| retry_realistic | 126 | 0.147 | <1e-4 | BIMODAL |
| rex_no_oracle | 126 | 0.147 | <1e-4 | BIMODAL |
| **rex** | 126 | **0.033** | **0.42** | **unimodal** |

A2/deepseek-v4-pro reproduces the pattern (all weak conditions p<1e-4; rex D=0.025,
p=0.78). Pooled-across-conditions is bimodal (mixture artifact). rex/runs n=12:
D=0.188, p=1e-4 (small-n, flagged).

## Finding
Bimodality (pass/fail spikes at reward 0 and 1) is a property of the **weak
policies**. REx collapses the lower/failure mode — ~90% of REx episodes land at
reward>=0.9, frac_mid≈0.10 — so REx's reward distribution is statistically
**unimodal near 1.0**. The dip test thus gives a quantitative signature of what REx
does: it doesn't just shift the mean, it eliminates the failure mode.
