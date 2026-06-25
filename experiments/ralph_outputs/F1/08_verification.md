# 08 — Verification against success criteria

| # | Success criterion (from 01_plan) | Status | Evidence |
|---|---|---|---|
| 1 | `related_work.md` parses as markdown with `## 2. Related Work` + subsections | PASS | validator T1: `has_heading_2_related_work: True`, `subsection_count: 7` |
| 2 | Every required citation present & correctly positioned vs C1/C2/C3 | PASS | 19/19 tokens present (T1); positioning traced to repo in 06 |
| 3 | Validator passes (coverage + structure) | PASS | T1 `ok: True / PASS / exit 0`; T2 compile OK |
| 4 | No shared core file edited | PASS | T4 — all writes under F1/; rex/sim/agent diffs predate the task |

## Are the outputs REAL (not placeholder)?
- `related_work.md` is a complete ~1,930-word prose section with 7 substantive
  subsections, an intro that maps each citation thread to the paper's three claims, and a
  positioning summary table. Not a stub.
- Every positioning claim is grounded in an actual repo file or grounding doc:
  - AutoHarness framing ← `rex/harness_synth.py` docstring (rules-as-data, held-out acc).
  - REx Thompson-tree ← `rex/tree.py` (`Beta(alpha,beta)`, sample-argmax-expand).
  - Deterministic reward / LLM-judge contrast ← `rex/scoring.py` (formula + `JUDGE_MODE`).
  - SREGym arXiv id 2605.07161 ← `PAPER_QUESTIONS.md §6`.
- `check_related_work.py` is a real, runnable, stdlib-only validator (compiles, runs,
  exits 0) — not pseudocode.

## Required-citation coverage (explicit)
CWM ✓, Code as Policies ✓, AutoHarness ✓, REx ✓ (+Reflexion/Self-Refine ✓), SREGym ✓
(+AIOpsLab/ITBench ✓), FIREBALL ✓, GRPO ✓, RLVR ✓, Constitutional AI ✓, LLM-as-a-Judge ✓,
pass@k ✓, Wilson ✓, McNemar ✓.

**Verdict: all four success criteria met with real, validated artifacts.**
