# B15 — Our pass@1 vs SREGym: a calibrated comparison (NOT a ranking)

_Generated 2026-06-25. Tables auto-rendered by `gen_comparison.py` from real A1/A2 run
artifacts and a cited `sregym_reported.json`. Read the caveats — the two benchmarks are
**not equivalent**, and the headline must not be read as "we beat SREGym."_

## TL;DR

- Our strongest number, **REx pass@1 ≈ 0.90** (A1 glm-5p2; A2 deepseek-v4-pro 0.89), is produced
  by a **multi-attempt tree search with oracle feedback** on a **state-machine simulator**.
- SREGym's best entry, **Claude Code E2E = 60.7%** (Sonnet 4.6, no noise), is produced by a
  **single-attempt** agent loop on **live containerized faults**, verified by a mitigation oracle.
- These are **different regimes on different substrates**. REx has **no SREGym counterpart**
  (SREGym permits one attempt per run). The fair single-attempt comparators from our suite are the
  `best_of_n` / `rex_no_oracle` band (**≈ 0.31–0.34**), which sit **below** SREGym's E2E range
  (32.9%–60.7%, no noise) — i.e. **SREGym's live tasks look materially harder than our simulator's
  single-run conditions.**
- The one robust, direction-agreeing finding across both benchmarks: **novel / unseen failure
  modes are the hardest** (SREGym E2E collapses ported→new; our single-attempt baselines also
  degrade off the simple family).

## Metric-equivalence note

SREGym reports "success rate" over **3 runs, single attempt per run**. A single-attempt success
rate **is** pass@1 — SREGym simply does not use the label. So SREGym's diagnosis / mitigation /
E2E success rates are directly comparable, *as pass@1*, to our pass@1. The **closest** SREGym
column to our reward is **E2E** (correct diagnosis AND mitigation), because our scalar reward
bundles SLO-restored + root-cause-cleared + no-collateral — it spans diagnose+mitigate. We cannot
report a diagnosis-only number (our reward is not decomposable), so we never compare to SREGym's
diagnosis-only column as if like-for-like.

---

<!-- TABLES: see comparison_table.md, reproduced below -->

## Table 1 — Headline cross-benchmark (overall pass@1)

Our pass@1 = fraction of (incident x seed) where graded reward >= 0.8 (SLO restored + root cleared + no collateral). SREGym E2E = correct diagnosis AND mitigation, oracle-verified, single attempt/run (== pass@1 semantics).

| Our condition | A1 pass@1 (glm-5p2, n=42) | A2 pass@1 (deepseek-v4-pro, n=30) | Attempt regime |
|---|---|---|---|
| `zero_shot` | 23.0% | 24.0% | single-shot (1 plan) |
| `best_of_n` | 34.1% | 30.7% | single-run-ish (best of N samples) |
| `retry_realistic` | 34.9% | 31.3% | single-run-ish (self retry) |
| `rex_no_oracle` | 33.3% | 28.7% | single-run-ish (tree, no oracle) |
| `rex` | 89.7% | 89.3% | MULTI-ATTEMPT + ORACLE (no SREGym counterpart) |

| Reference: SREGym (90 live tasks, single attempt/run) | E2E success |
|---|---|
| Range across agents, **no noise** | 32.9% – 60.7% |
| Range across agents, **with noise** | 30.4% – 53.7% |
| Best single entry (Claude Code, Sonnet 4.6, no noise) | 60.7% |

> **Caption:** "E2E range" is the spread across leaderboard agents, NOT a confidence interval. Our `rex` row (multi-attempt + oracle) has **no SREGym counterpart** — SREGym allows one attempt per run — and must not be read as "beating" SREGym. The fair single-attempt comparators are the `best_of_n`/`rex_no_oracle` band.

## Table 2 — LOOSE ANALOGY (not a validated mapping): family ↔ partition

Mapping simple↔Ported, cascade↔Similar, novel↔New is an **unvalidated analogy**; only novel↔New (both = unseen failure modes) is defensible. No tasks are shared.

| Family (ours) | rex pass@1 (A1) | rex_no_oracle pass@1 (A1) | ↔ SREGym partition | SREGym E2E (Claude Code, no noise) |
|---|---|---|---|---|
| `simple` | 88.9% | 72.2% | `ported` | 60.8% |
| `cascade` | 85.0% | 15.0% | `similar` | 70.5% |
| `novel` | 100.0% | 23.3% | `new` | 28.2% |

> Both benchmarks agree directionally on ONE thing: **novel/unseen failures are hardest.** SREGym E2E collapses on `new` (Claude Code 60.8%→28.2% ported→new); our single-attempt `rex_no_oracle` is also weakest off the simple family.

---

## Caveats — axes of non-equivalence (read before citing any number)

1. **Substrate.** SREGym = live Kubernetes microservices with injected high-fidelity faults
   (some ported from AIOpsLab/ITBench). Ours = a deterministic state-machine simulator
   (`sim/engine.py`). A 0.90 in sim is **not** evidence of resolving 90% of real incidents.
2. **Grader.** SREGym uses a checklist LLM-judge (diagnosis) + a **live mitigation oracle**
   (does the real system recover?). Ours uses a hand-authored graded reward thresholded at **0.8**.
   Different definitions of "success."
3. **Attempt budget.** SREGym = **1 attempt per run**. Our headline `rex` = **multi-attempt tree
   + oracle feedback**. This is the single biggest non-equivalence: REx has no SREGym analogue.
4. **Oracle feedback.** REx receives an oracle signal between attempts; SREGym agents iterate only
   on self-observed signal within one run. The fair within-suite analogue is therefore
   `rex_no_oracle` (0.33), not `rex` (0.90). The 0.90→0.33 drop *is* the oracle's contribution.
5. **Threshold knob.** Our pass@1 thresholds a continuous reward at 0.8; slide the cutoff and our
   pass@1 moves. SREGym's binary oracle has no such knob. Treat our pass@1 as cutoff-dependent.
6. **Metric decomposition.** SREGym separates diagnosis vs mitigation (and shows they diverge,
   e.g. Claude Code 72.6 diag vs 75.6 mit). Our single scalar cannot be split; we only map to E2E.
7. **Models differ.** SREGym: Sonnet 4.6 / GPT-5.4 / Kimi K2.5. Ours: glm-5p2 (A1) /
   deepseek-v4-pro (A2). No shared model; cross-model deltas confound any "method" comparison.
8. **Noise.** SREGym reports with/without observability noise and degrades under noise
   (Claude Code E2E 60.7→53.7). Our sim is effectively **noise-off**, so the honest SREGym
   comparator is the **no-noise** column; we are not testing observability robustness.
9. **Task counts & overlap.** SREGym = 90 problems; ours = 42 (A1) / 30 (A2). **Zero shared
   tasks.** Side-by-side display only; no paired statistics across benchmarks are possible.
10. **Family↔partition mapping is a loose analogy.** simple↔Ported / cascade↔Similar / novel↔New
    is unvalidated; only **novel↔New** (both = unseen failure modes) is defensible. We do not
    compute per-partition win/loss deltas.

## Honest bottom line

If forced to a one-line comparison: **our single-attempt baselines (≈0.31–0.34 pass@1) under-
perform SREGym's single-attempt agents (E2E 32.9%–60.7%, no noise)**, which is consistent with
SREGym's live tasks being harder than our simulator's. **REx's 0.90 is a genuine lift, but in a
different regime (multi-attempt + oracle) that SREGym does not measure**, so it cannot be claimed
as a SREGym result. Both benchmarks independently confirm that **novel failures are where agents
break down.**

## Sources

- SREGym paper: arXiv:2605.07161v1, "SREGym: A Live Benchmark for AI SRE Agents with High-Fidelity
  Failure Scenarios" (https://arxiv.org/html/2605.07161v1). Diagnosis 38.9–72.6%, mitigation
  57.3–78.5%, E2E 30.4–60.7%; 90 problems (Ported 34 / Similar 43 / New 13); 3 runs/problem,
  single attempt/run; per-partition collapse on `new`.
- SREGym leaderboard: https://sregym.com/leaderboard (8 entries, retrieved 2026-06-25).
- Our numbers: `experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json` (full-42,
  3 seeds, deterministic judge, threshold 0.8, floor_ok) and
  `experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json` (30 inc, 5 seeds).
- Reward semantics: `rex/scoring.py`, `rex/eval_pass_at_k.py` (THRESHOLD = 0.8).
