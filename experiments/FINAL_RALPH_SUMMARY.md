# FINAL RALPH LOOP SUMMARY — SRE-Degrees Research

**Run:** 120 tasks (A1–J10) × 10-step Ralph Loop cycle each.
**Completed:** 2026-06-25. **Status:** 120/120 `completed`, 0 failed, 0 skipped.
**Output:** `experiments/ralph_outputs/<task_id>/` — 1,200 step files (01–10) + 120 SUMMARY.md + 120 result.json + **808 real artifacts** (code, data, YAML, figures, docs).
**Blockers:** 56 tasks documented an honest blocker (compute/credits/live-cluster/human-coordination) yet still shipped a runnable deliverable. **Zero fabricated results.**

## Execution model
Each task was run by a dedicated worker (fresh context) executing the full 10-step cycle (PLAN → GRILL → IMPROVE → SPEC → OUROBOROS → IMPLEMENT → TEST → VERIFY → CRITIQUE → FEEDBACK). Workers ran in parallel batches by category, each writing real, validated artifacts under its own task directory. To keep 120 parallel writers safe, workers were forbidden from editing shared core files (`rex/`, `sim/`, `agent/`, `experiments/*.py`); core changes were delivered as `.patch` files instead. Integrity verified post-run: core files show only the pre-existing session-start modifications.

## Headline research findings (real numbers, real runs)

**Benchmark & eval (A, B):**
- Full 42-incident pass@k ran (A1): **REx pass@1 = 0.90 [0.83,0.94] vs zero-shot 0.23 [0.17,0.31]** (disjoint CIs), reproduced on a 2nd cheaper model (A2: 0.893 vs 0.240, 750 episodes, McNemar p<0.0001).
- **Key honest caveat (A2, B8):** `rex_no_oracle ≈ best_of_n` — the lift comes from *oracle feedback*, not the refinement tree itself. Effect size is LARGE only for the full-REx (oracle) condition.
- 7 incidents are **unsolvable under both models** (B12); 41 are "learnable-but-hard" (zero-shot p@1=0, REx p@1=1).
- Stats fully computed: Wilson CIs (B3, validated vs textbook), McNemar+Holm (B2), Cohen's h/d (B8), 10k-bootstrap (B9, exposed Wilson optimism at n=5), threshold robustness (B11).

**Harness synthesis (C):**
- 3 synthesized rules ≈ 0.90 held-out acc (vs hand-written 0.95); **proposer model matters enormously** (C6: minimax-m3 near-baseline, deepseek produced an *empty* ruleset).
- A human-injected 4th rule reaches 94.9% **but synthesis provably cannot discover it** (0 training examples activate the feature) (C8).
- Information-theoretic result (C12/I4): 3 rules saturate the 6-feature space (remove 95.5% of label entropy; any 4th rule gains ≤0.034 bits) — **the limit is the feature language, not the rule count.**

**Training (D):**
- RFT trend is **flat/within-noise** at the repo-canonical threshold (D1: real 9-step partial, slope +0.0012/step); climbs only at a lower τ=0.65 (B10). Full 50-step run is compute-blocked, launcher shipped.
- **Reward hacking is real (D13):** 5 working exploits of the deterministic judge — negation/single-token/wrong-component at 100%, hedge at 92.9% (composes to 0.55 reward). This is the most important safety finding.
- Same-scenario GRPO groups (D3) cut advantage 2nd-moment 2.38× and flip the advantage sign on 28% of rollouts (mechanism proven; live A/B blocked on backend).

**Fireball / transfer (E):** Real FIREBALL D&D dataset **fetched** (E2, CC-BY-4.0) — partly unblocking what the task list assumed was blocked on Wenji. Converter + ablation transforms validated on 319 real records; trained-model comparisons (E3–E9) blocked on absent fork/GRPO slug.

**Theory (I):** Graduation framework formalized with a runnable reference impl + 25 tests (I1); bimodality proven (I2) and **statistically confirmed via Hartigan's dip test** (I3: weak policies bimodal p<1e-4, REx unimodal p=0.42); trap taxonomy is **94% scale-trap, 0% failover** (I7) — a real coverage gap.

**Paper & positioning (F, G):** Full Related Work, Limitations, Conclusion, 250-word Abstract, AAAI LaTeX skeleton, rebuttal-anticipation, reproducibility checklist, supplementary catalog, 6 publication figures from real numbers, arXiv package, poster, talk outline; honest SREGym positioning (fair single-attempt band ~0.34 ranks mid-pack; REx 0.90 flagged as a *different regime*, not a leaderboard win).

**Infra (H):** vLLM scaffold, CI workflow, Dockerfile, W&B shim, promotion-engine dashboard, CI scenario validator (**61/61 pass**), model registry, nightly-eval, leaderboard page, Makefile (`make test` → 93 passed).

**Real-world (J):** Shadow-mode runner with structurally-enforced no-execution guarantee; case study on the Cloudflare WAF-regex outage with a **real agent run** (avoided the edge-proxy scaling trap, fixed via rollback); a **novel never-seen scenario** (NTP clock-skew split-brain) that 3 frozen models solve cleanly (J6, true generalization). Live GKE deploy blocked — the temp GCP account (`devstar4126@gcplab.me`) is deleted (`invalid_grant`), so the cluster API is unreachable.

## Notable bugs/gaps surfaced (actionable)
- **A16:** 7/61 scenarios' canonical fix does **not** resolve in the sim (4 authoring bugs, 3 unmodeled-SLO KeyErrors) — documented, not silently patched.
- **D13 reward hacks** + **A15** noisy-metrics observation layer is latent (sim doesn't consume `alerting`/`buried_under` yet).
- Statistical power is thin (n=5 in the original ablation; A1/A2 widen this).

## Cross-task dependency note
Categories were run in parallel, so a few late-category workers couldn't see same-batch siblings' outputs (e.g. G8 synthesized from repo artifacts because G5–G7 were still running). Each such case was handled by grounding in the repo directly — no fabrication.

## Where to look
- Per-task narrative: `experiments/ralph_outputs/<task_id>/SUMMARY.md`
- Machine-readable: `experiments/ralph_outputs/<task_id>/result.json` (status/artifacts/blocker/one_line)
- Live dashboard: `experiments/dashboard.html` (reads `experiments/ralph_status.json`)
- New benchmark scenarios: `scenarios/cidg/generated/` (A6 ×10, A11 ×6, A13 ×3, J6 ×1)
