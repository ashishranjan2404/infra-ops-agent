# 06 — Implementation

## What I built (all task-namespaced; NO shared-core edits)

### 1. `artifacts/graduation_framework.md` (11.2 KB) — the primary deliverable
A rigorous formalization of "earning autonomy":
- **§1 Primitives** reused verbatim from `rex/scoring.py::failed_checks`, `rex/loop.py`
  (`clean_win`), `rex/escalate.py` (escalation as a win), `rex/harness.py`
  (`singleton_node_notready` = unsolvable).
- **§2 Trust tiers** T0 Observer ⊂ T1 Restarter ⊂ T2 Scaler ⊂ T3 Operator, keyed to action
  blast radius, with the action→tier map grounded in the tools graded/gated by the harness.
- **§3 Batch statistics** over a held-out distribution with a Wilson lower bound.
- **§4 Graduation predicate** — conjunctive (Wilson-LB clean-win ≥ θ_T, esc-rate ≥ ε_T,
  hard-zero unblocked trap, n_min, escalation actually tested).
- **§5 `EarnedAutonomy(π,T,S)`** — the headline predicate + `grant` + a soundness sketch
  (rule-of-three harm bound tightening with tier).
- **§6 Revocation** — instant/asymmetric, with audit reasons.
- **§7 Four worked examples** on the real ARCHITECTURE.md numbers (0.86 = 4 clean + 1
  escalation; why live n=5 is provisional; the REx compression result; the blocking trap).
- **§8 Honest scope/limits.**

### 2. `artifacts/graduation.py` (≈ 200 LOC) — executable reference impl
Pure Python, no deps, no network/LLM. Implements every predicate so the math is *runnable*:
`TIERS`, `clean_win`, `correct_escalation`, `wilson_lb`, `tier_metrics`, `graduated`,
`earned_autonomy`, `grant`, `revoke`, and `outcome_from_loop_result` — an adapter that maps a
real `rex/loop.py::refine_loop` / `rex/tree.py` result dict into a committed `Outcome`. It
reuses the EXACT `failed_checks` vocabulary and `clean_win` semantics from the core, but
deliberately does NOT import or edit any core file (parallel-safe, self-contained).

### 3. `artifacts/test_graduation.py` — 25 pytest cases
Validates internal consistency (Wilson monotonicity/tightening, clean-win/escalation logic,
tier map, graduation conjunction, monotone earned-autonomy, revocation triggers, the loop
adapter) AND the two worked examples (live n=5 → provisional T0; scaled to n_min → T1).

## Why no core files were touched
The task is conceptual/formal. The reference impl *mirrors* core semantics rather than
importing them, so it is a standalone artifact under `I1/artifacts/`. If one wished to wire
this into the live harness, the integration point is documented: feed each
`refine_loop`/`tree` result through `outcome_from_loop_result(...)` and aggregate with
`grant(...)`. That wiring would be a proposed change to a new module (e.g.
`rex/graduation.py`) — NOT an edit to existing core files — and is left as a noted next step,
not performed, per the parallel-safety rules.

## Design decisions traceable to the grill / ouroboros
- Conjunctive predicate + hard-zero trap gate (PSRE/SMR; ouroboros P3).
- Graduation on committed plan, not best-of-budget existential (AAAI/RLE).
- Wilson LB so small n can't graduate (SMR); live n=5 → only provisional T0 (ouroboros P4).
- Escalation gate requires |UNSOLV| ≥ 1 (ouroboros P2).
- `B_{S,T}` = filter by minimal sufficient tier (ouroboros P1).
- Asymmetric instant revocation with audit reason (DOL).
- Enforcement-agnostic grant output (SMR).
