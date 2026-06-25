# F2 — Evidence Index for LIMITATIONS.md

Every empirical claim in `LIMITATIONS.md` traces to a real repo artifact.

| Limitation | Anchor fact | Source file | Verified |
|---|---|---|---|
| L1 | 42 incidents (10 + 32 generated); 51 YAMLs on disk | `experiments/FINAL_SUMMARY.md` (P1); `scenarios/cidg/generated/*.yaml` (glob=51) | yes (glob counted) |
| L1 | spec fields topology/root_cause/fault/trap_actions/canonical_fix | `experiments/build_incidents.py`; any `scenarios/cidg/generated/*.yaml` | yes |
| L2 | reward = 0.30·diag + 0.25·fix + 0.45·resolved; author keyword oracle | `rex/scoring.py` (line 4, 22: W_ROOT=0.30,W_FIX=0.25,W_RESOLVED=0.45) | yes (grep'd) |
| L2 | fool-rate is oracle-relative | `experiments/ralph_outputs/D13/SUMMARY.md` ("Honest caveats") | yes |
| L3 | v1 0.522→0.491 (−0.031); v2 0.504→0.541 (+0.037); 15 steps, 10 tasks; std~0.18 | `experiments/FINAL_SUMMARY.md` (P4 table) | yes |
| L4 | 294 probes, 5 exploit classes, hedge 92.9% fool-rate, cap 0.30 | `experiments/ralph_outputs/D13/SUMMARY.md` (attack table) | yes (92.9 grep'd) |
| L4 | composed hedge+real-fix = 0.55 | `experiments/ralph_outputs/D13/SUMMARY.md` | yes |
| L5 | single domain (k8s/cloud SRE) | `experiments/CLAIMS_EVIDENCE.md`; all scenario YAMLs | yes |
| L5 | Fireball P7 BLOCKED, corpus + GRPO branch not in repo | `experiments/FINAL_SUMMARY.md` (P7) | yes |
| L6 | ablation 0.242/0.235/0.230/0.250 vs 0.687 | `experiments/CLAIMS_EVIDENCE.md` (Claim 3); `rex/runs/ablation.json` | yes |
| L6 | 750-episode run partial (API latency) | `experiments/FINAL_SUMMARY.md` (P3) | yes |
| L6 | single-model (Haiku), SME feedback semi-synthetic | `experiments/CLAIMS_EVIDENCE.md` | yes |
| Scope | harness 66.7%→89.7%→94.9%, false-allow 100%→30.8% | `experiments/tables/table3_harness_synthesis.md`; `experiments/FINAL_SUMMARY.md` (P5) | yes |
| Scope | REx-SME 0.242→0.687 (2.8×) | `rex/runs/ablation.json`; `experiments/CLAIMS_EVIDENCE.md` | yes |

Checker: `check_limitations.py` asserts each source file exists and that the
generated-scenario glob ≥ 30; `07_test_results.md` additionally greps the 92.9%
canary from D13 to prove the citation is live, not invented.
