# I2 — 10 Feedback for the next task

The biggest lesson: when a task says "prove X induces a bimodal distribution,"
pin down *which* distribution and *which* operational definition of bimodality
before coding — the full mixed reward population in `rex/scoring.py` is
multi-modal (partial-credit fills the middle), and the clean two-atom result only
appears once you condition on the competent / resolved-eligible subpopulation.
Lead with the conditioned law for the proof and report the full histogram as
descriptive, or a reviewer will (rightly) call the claim misleading. Also separate
"a valley exists" from the *economically meaningful* threshold — here the sharp,
defensible line is `TRAP_PENALTY > W_RESOLVED` (the basin drops to/below the
unresolved-clean reward `MAX_CLEAN − W_RESOLVED`), which holds for the shipped
0.60 vs 0.45. Two concrete reusable habits: (1) assert any mirrored constants
against the real source file (`rex/scoring.py`) so the artifact can't silently
drift, and (2) don't gate conclusions on Sarle's BC for bounded/discrete support —
it reads "unimodal" even when a clean valley exists; the largest-gap valley test
is the honest primary metric. Next task should, if it touches reward shape
empirically, run real rollouts via `rex/eval_pass_at_k.py` on the CIDG scenarios
rather than synthetic draws.
