# 08 — Verification against success criteria

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| Covers all 3 paradigms × 5 axes, correct & defensible | ✅ | `comparison.md` §2 + summary matrix; `axes_matrix.json` 15 cells |
| Code-as-policy column grounded in named real files | ✅ | cites `agent/llm.py`, `rex/harness.py`, `rex/loop.py`, `rex/tree.py`, `rex/scoring.py`, `sim/engine.py`, `scenarios/cidg/generated/*.yaml`; all `repo_citations` resolve (validator T4) |
| RLHF characterized accurately | ✅ | reward model + PPO + **KL-to-reference**; Christiano 2017 / InstructGPT cited |
| CAI characterized accurately | ✅ | **two stages**: SL-CAI self-critique/revise + RLAIF (AI preference model); Bai et al. 2022 cited |
| `axes_matrix.json` parses | ✅ | validator T1, exit 0 |
| `validate_matrix.py` exits 0 (shape + non-empty + paths) | ✅ | `07` — `EXIT=0`, incl. negative self-tests |
| Honest limitations section (where code-as-policy loses) | ✅ | `comparison.md` §4 (no verifier → no method; frozen-model ceiling; opex; verifier bugs) |

## Are the outputs real (not placeholder)?
Yes. `comparison.md` is a full ~11.5 KB essay with substantive, paradigm-specific content (not
lorem/TODO). `axes_matrix.json` has 15 distinct, non-trivial cell strings. `validate_matrix.py` is a
runnable program that genuinely passes AND demonstrably rejects bad input. Repo-grounding claims were
cross-checked against the actual `rex/scoring.py` and `rex/tree.py` source.

## Accuracy guardrails honored
- No invented numbers: efficiency stated as orders of magnitude ("tens of thousands of comparisons,
  varies by setup"); the one repo-internal figure (~0.86 ceiling) is attributed to repo files, not
  presented as universal.
- No overclaiming: the doc explicitly states code-as-policy is **not** generally superior — it needs
  a verifier and inherits the model ceiling.

## Constraint compliance
No shared core file edited. All artifacts live under `experiments/ralph_outputs/I8/`. Stdlib-only,
no network/cluster/GPU dependency.
