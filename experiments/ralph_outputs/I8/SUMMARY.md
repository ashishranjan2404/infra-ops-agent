# SUMMARY — Task I8

**Task:** rigorous theoretical comparison of code-as-policy vs RLHF vs Constitutional AI across five axes (knowledge location, verifiability, sample efficiency, safety guarantees, interpretability), grounded in this project's code-as-policy / auto-harness approach.

**Status:** completed.

## Deliverables (all under experiments/ralph_outputs/I8/)
- artifacts/comparison.md — ~11.5 KB essay: unifying frame ("where normative knowledge lives") -> precise definitions w/ references -> 5 axes x 3 paradigms -> summary matrix -> honest "where code-as-policy LOSES" -> synthesis. Grounded in real repo files.
- artifacts/axes_matrix.json — machine-readable 3x5 matrix + 8 resolvable repo citations + not_a_scorecard/key_caveat flags.
- artifacts/validate_matrix.py — stdlib validator (shape, non-empty cells, citations resolve, required core files cited) with negative self-tests. Exits 0.
- 01..10 step files (plan -> grill -> improved plan -> spec -> ouroboros -> implementation -> tests -> verification -> critique -> feedback).

## Key claims
- RLHF = reward model + PPO + KL-to-reference; knowledge in weights (learned, gameable proxy).
- CAI = two stages (SL-CAI self-revision + RLAIF AI-preference model); weights + legible constitution.
- Code-as-policy (this repo) = verifier-guided inference-time search over a frozen swappable model + rejection safety gate; knowledge in git-diffable code (rex/scoring.py reward, rex/tree.py thompson_search, rex/harness.py gate). Ground-truth reward but task-conferred not method-conferred; inherits the model ceiling; opex-heavy.
- Explicitly NOT a scorecard: each paradigm is best in its native domain.

## Verification
validate_matrix.py -> EXIT=0 (15 non-empty cells, 8 citations resolve, negative self-tests reject bad input). Markdown probes pass. Grounding cross-checked against live rex/scoring.py and rex/tree.py. No shared core file edited.
