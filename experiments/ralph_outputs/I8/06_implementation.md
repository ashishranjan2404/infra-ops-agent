# 06 — Implementation

## What I built (all task-namespaced; no shared-core edits)

1. **`artifacts/comparison.md`** (~11.5 KB) — the deliverable essay. Covers all 3 paradigms ×
   5 axes, grounded in this repo's real code-as-policy stack. Structure: unifying frame → precise
   definitions (with references) → the 5 axes → summary matrix → "where code-as-policy LOSES" →
   synthesis. Incorporates every accepted critique from 03/05:
   - CAI described as **two stages** (SL-CAI self-revision + RLAIF).
   - RLHF includes the **KL-to-reference** penalty.
   - **Verifiability is flagged as task-conferred, not method-conferred.**
   - **Frozen-model ceiling** stated honestly (repo numbers attributed to `ARCHITECTURE.md` /
     `rex/frontier.py`, not floated as universal).
   - Sample efficiency framed as **amortized capex vs per-call opex**, numbers kept qualitative.
   - Interpretability nuanced **both directions** (CAI constitution is legible; code reward can be
     a bug surface).
   - Explicit **"not a scorecard"** caveat.

2. **`artifacts/axes_matrix.json`** — machine-readable 3×5 matrix (`cells[paradigm][axis]`), plus
   `repo_citations` (8 real files), a `not_a_scorecard` flag, and the `key_caveat`. Mirrors the
   essay so the prose and the structured data can't silently diverge.

3. **`artifacts/validate_matrix.py`** — stdlib-only validator. Checks: JSON parses (T1); paradigm/
   axis sets exact (T2); every cell present + non-empty (T3); every citation path resolves under the
   repo root found by walking up to `.git` (T4); required core files cited (T5). Adds **negative
   self-tests** that mutate a copy (blank a cell, inject a bad path) and assert rejection — so a
   green run proves the validator actually catches violations.

## Grounding verified against real repo state
`rex/scoring.py` confirmed to implement `W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25,
0.45, 0.60` with a **deterministic** judge (matches the essay's anti-reward-hacking claim).
`rex/tree.py` confirmed to implement `thompson_search` (Thompson-sampling tree over refinement
candidates — matches the "verifier-guided inference-time search" characterization). `agent/llm.py`
+ `agent/models.py` are the frozen, swappable policy interface. No shared file was modified.

## Commands run
- `python3 validate_matrix.py` → exit 0 (see `07_test_results.md`).
- JSON + markdown sanity probes → pass.
