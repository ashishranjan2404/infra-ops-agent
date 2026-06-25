# A7 — 08 Verification

## Against the success criteria (01 / 03)
1. **Runs clean on all real YAMLs, valid JSON+CSV** — YES. 48/48 scored, JSON
   parses, CSV well-formed, `count==disk` every run.
2. **Both metrics in [0,1] with meaningful spread** — YES.
   expected_pass_rate 0.433–0.873; trap_complexity 0.062–0.791. Not degenerate.
3. **Face-valid ranking** — YES. Synthetic single-node leaf incidents
   (`*-leaf-*`, redis-cache-flush) cluster at the easy end (epr 0.873, tc 0.062);
   multi-node cascading postmortems (gitlab-db-deletion, aws-s3-typo-capacity,
   cloudflare/github network partitions) cluster hard (epr ≈ 0.43, tc ≈ 0.78).
4. **Zero mutation of source YAMLs / core .py** — YES. T7 confirms source mtimes
   unchanged; only files written are under `experiments/ralph_outputs/A7/
   artifacts/`. No `rex/`, `sim/`, `agent/`, `experiments/*.py` touched.

## Are outputs real (not placeholder)?
YES. `difficulty_scores.json` (48 entries with full per-component breakdowns)
and `difficulty_scores.csv` are generated from the live corpus by the committed
script. Every number is reproducible by re-running `score_difficulty.py` (T5
idempotency: identical md5 across runs).

## Auditability check
Spot-check `cloudflare-waf-regex` (tc=0.738): breakdown =
topology 0.12 (4 nodes) + fanout 0.05 (3 edges) + cascades 0.16 +
loudest_not_cause 0.16 + hidden_root 0.12 + buried_gun 0.096 (buried_under 40) +
trap_actions 0.02 + severity 0.042 = 0.738. Matches the emitted value — weights
reproduce the score, satisfying the AAAI auditability requirement from the grill.

## Verdict
Deliverable meets all success criteria. The only non-empirical aspect
(uncalibrated prior) is documented honestly in 09, not hidden.
