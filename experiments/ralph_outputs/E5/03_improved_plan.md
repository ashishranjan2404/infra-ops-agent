# E5 — Improved Plan (post-grill)

## What changed vs 01_plan.md
1. **Record family + failure_class-reuse per incident** (PSRE/SMR). The harness keeps
   the A8 `family` and the tier3 `failure_class_seen_in_train` flag in scope so the
   report can be read per-family and is not collapsed into one hero number.
2. **Controls are first-class and load-bearing** (AAAI/RLE). `empty` is the floor
   (must be pass@1 == 0); `oracle` is BOTH a ceiling and a **data-validity check** —
   if oracle does not reach 1.0 on an incident, that incident's gold fix is
   unreachable and its pass@1 is untrustworthy. The harness emits a `floor_ceiling`
   block asserting `floor_ok` and `ceiling_ok`.
3. **Real baselines are mandatory** (DOL). Even with Fireball blocked, the harness
   runs at least one reachable roster model (glm-5p2) so the artifact is independently
   useful. Unreachable policies are recorded `status=blocked` with the error, never
   silently dropped.
4. **Fireball handled explicitly** (RLE/AAAI/DOL). `--fireball-model` / `$FIREBALL_MODEL`
   resolves the transfer target; if it is not in `ROSTER` or is unreachable, it is
   recorded blocked with the concrete reason. No fabricated transfer delta.

## Critiques accepted
- Per-family disclosure (PSRE) — accepted; the set composition and per-key family are
  written into `transfer_results.json` and `08_verification.md`.
- Deterministic judge + CI + std (RLE/AAAI) — accepted; uses P0 `score_plan` and
  Wilson CI from `compute_pass_at_k`.
- Oracle as data-validity control (AAAI) — accepted; `ceiling_ok` gate added.
- Ship real baselines (DOL) — accepted; glm-5p2 run live.

## Critiques rejected (with reason)
- RLE's "oracle ceiling is trivial, drop it" — **rejected.** AAAI's rebuttal stands:
  oracle is cheap and validates that the novel incidents are *solvable at all* under
  this harness. A novel incident the oracle can't pass would silently zero every
  policy. Keep it as a validity gate, while agreeing it is a weak *model-quality*
  ceiling.
- "Re-derive a fresh novel split for E5" — **rejected.** The brief says reuse A8 if
  present; re-deriving would duplicate A8's tiered guard and risk an inconsistent set.

## Net plan
Reuse A8 → select 10 (novel-first, back-fill simple, assert loadable) → run `empty`,
`oracle`, `glm-5p2` (real), `fireball` (blocked) → deterministic pass@1 + CI + std,
per-family aware, floor/ceiling gated → write `transfer_results.json` + docs.
