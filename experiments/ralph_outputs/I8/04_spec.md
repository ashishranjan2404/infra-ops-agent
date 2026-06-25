# 04 — Spec

## Artifact 1: `artifacts/comparison.md`
Markdown essay. Section structure fixed per 03. Hard requirements:
- Every paradigm characterized with a primary reference:
  - RLHF → Christiano et al. 2017 (deep RL from human preferences); InstructGPT (Ouyang et al. 2022).
  - CAI → Bai et al. 2022, "Constitutional AI: Harmlessness from AI Feedback" (Anthropic).
  - Code-as-policy → this repo + the auto-harness / code-world-model lineage (DeepMind code-as-verify).
- Code-as-policy claims must cite real repo paths: `agent/llm.py`, `rex/harness.py`, `rex/loop.py`,
  `rex/tree.py` (`thompson_search`), `rex/scoring.py` (the weighted reward), `sim/engine.py`,
  `scenarios/cidg/generated/*.yaml`.
- Must contain a "where code-as-policy LOSES" section.

## Artifact 2: `artifacts/axes_matrix.json`
Schema (validated by Artifact 3):
```json
{
  "paradigms": ["code_as_policy", "rlhf", "constitutional_ai"],
  "axes": ["knowledge_location", "verifiability", "sample_efficiency",
           "safety_guarantees", "interpretability"],
  "cells": {
    "<paradigm>": { "<axis>": "<non-empty string>" , ... },
    ...
  },
  "repo_citations": ["agent/llm.py", "rex/scoring.py", "..."]
}
```
Contract:
- `cells` has exactly one entry per paradigm, each with exactly one entry per axis.
- Every cell value is a non-empty string.
- Every path in `repo_citations` resolves to a real file under the repo root.

## Artifact 3: `artifacts/validate_matrix.py`
Signature / behavior:
```
python3 validate_matrix.py            # validates the sibling axes_matrix.json
-> exit 0 + "OK: ..." on success
-> exit 1 + first failure reason on any violation
```
Test cases (asserted in-script):
- T1: JSON parses.
- T2: `paradigms` == 3 expected, `axes` == 5 expected.
- T3: every (paradigm, axis) cell present and non-empty (stripped len > 0).
- T4: every `repo_citations` path exists relative to repo root (walk up to find `.git`).
- T5: at least the core code-as-policy files are cited
  (`rex/scoring.py`, `rex/tree.py`, `agent/llm.py`).

## Repo root discovery
`validate_matrix.py` finds repo root by walking parents until a dir containing `.git` is found,
so it runs correctly from `artifacts/`.
