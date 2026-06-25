# A1 — 09 Critique (honest)

## What a reviewer attacks
1. **Single model.** The full-42 table is glm-5p2 only. The `--frontier` path (5 models) was
   NOT run — it would be ~5× the 27 min and risks other gateway models being unavailable. So the
   "REx >> baseline on the full set" claim is established for one model; cross-model generalization
   is still the 15-incident-slice frontier run, not the full 42. **Honest gap.**
2. **seeds=3.** Defensible for pass@1 (n=126 overall, tight CIs), but:
   - pass@5 is degenerate (saturates to 1.0 once an incident is ever solved) — labeled, not deleted.
   - per-family pass@1 rests on n=30–60; the per-family CIs are wide (e.g. rex novel [0.89,1.00]).
     A clean seeds≥5 rerun would firm these up. The runner supports `--seeds 5` directly.
3. **rex pass@1 = 0.90 is suspiciously high.** Is REx too strong, or the benchmark too easy at
   k=4 budget? The floor check rules out trivial reward-hacking (cheapest path < 0.8), and
   zero_shot at 0.23 shows the incidents are NOT trivially solvable, so the gap is real signal
   rather than a saturated benchmark. But novel pass@1=1.000 (std 0) on n=30 means REx solves
   every novel incident every seed — that *could* indicate the novel family is under-difficult
   for REx at this budget, which is worth probing (lower budget / harder novel incidents).
4. **rex_no_oracle ≈ baseline on cascades (0.15).** This is the honest, slightly *negative*
   finding: without the oracle feedback signal, REx's tree search barely beats best_of_n on the
   hard cascades. It's a real limitation of the method, not hidden — it's in the table.
5. **Job ordering / robustness.** The core sweep is condition-major; a mid-run timeout would have
   left `rex` empty. We got lucky (it finished), but the artifact documents the recommended
   `as_completed` core fix and the `--conditions zero_shot,rex` anchor-first fallback.

## What's weak
- Only one seed count, one model, one budget (N=4). No sensitivity sweep.
- pass@5 column is near-useless at seeds=3; kept only for schema completeness.
- The benchmark may be a touch easy for REx on `novel` (perfect score).

## What's solid
- All 42 incidents covered (was 15), deterministic judge, floor_ok, 0 errors, disjoint CIs
  between rex and zero_shot. The headline claim — *REx lifts pass@1 from 0.23 to 0.90 across the
  full 42-incident benchmark, with non-overlapping 95% CIs* — is real and reproducible via the
  task-namespaced runner.
