# 08 — Verification against success criteria

| Success criterion (from 01_plan) | Met? | Evidence |
|---|---|---|
| `graduation_framework.md` parses, defines tiers/graduation/revocation + the predicate | ✅ | 11.2 KB, parses; §2 tiers, §4 graduation, §5 EarnedAutonomy, §6 revocation |
| ≥ 2 worked examples tied to real project numbers | ✅ | §7 has 4 (live 0.86=4+1; provisional-T0; REx compression; blocking trap) |
| `graduation.py` imports | ✅ | `import graduation` OK, tiers [0,1,2,3] |
| `test_graduation.py` passes under pytest | ✅ | 25/25 passed in 0.01s |
| No shared-core file modified | ✅ | see check below |
| Grounded in thesis + `rex/escalate.py` / `rex/scoring.py` | ✅ | §1 cites failed_checks, clean_win, escalation_report, singleton_node_notready |

## Outputs are REAL, not placeholder
- `graduation.py` is executable and its predicates are exercised by 25 assertions — the math
  runs, it is not pseudocode.
- The Wilson bound, the conjunctive graduation gate, the asymmetric revocation, and the
  loop-result adapter are all concrete and tested.
- The worked examples decompose the project's *actual* headline (0.86 = (4×1.0+0.30)/5) into
  the per-incident outcome vector the framework consumes, and the test suite *proves* that
  decomposition graduates only provisional T0 at n=5 — a real, non-trivial, slightly
  counter-intuitive result, not a rubber-stamp.

## No-core-edit verification
The Real-artifact rules forbid editing `rex/*.py`, `sim/*.py`, `agent/*.py`,
`experiments/*.py`, status/dashboard, or other task dirs. All my writes are under
`experiments/ralph_outputs/I1/`. `graduation.py` *mirrors* core semantics (re-declares the
CHECKS tuple, re-implements clean_win) rather than importing core, so running it cannot touch
or import a shared module. Confirmed by `git status` showing only `I1/` additions (untracked),
no modifications to tracked core files.

## Self-consistency spot-check
- `grant([]) == 0` (no evidence → Observer only) ✓
- A perfect-quality but small (n=5) batch → T0; the same quality at n_min(T1)=20 → T1 ✓
  (evidence, not just quality, gates autonomy — the central claim).
- One unblocked trap zeroes graduation at its tier regardless of clean-win rate ✓
  (tail risk is gated hard, the PSRE/ouroboros requirement).
