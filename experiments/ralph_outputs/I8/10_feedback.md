# 10 — Feedback for the next task

Theory/writing tasks still benefit enormously from a real-artifact discipline: pairing the prose
with a **machine-readable mirror** (`axes_matrix.json`) and a **non-vacuous validator** (one that
includes negative self-tests proving it rejects bad input) turns "did you write something" into a
checkable pass/fail, and forces the prose and data to stay consistent. For grounded comparisons,
**cross-check every "this repo does X" claim against the actual source** before asserting it
(I confirmed the reward weights in `rex/scoring.py` and `thompson_search` in `rex/tree.py`) — it's
cheap and kills the biggest failure mode (citing files/behaviors that don't exist). Finally, on
opinionated comparisons the strongest move for credibility is a dedicated **"where my approach
loses"** section plus a **"not a scorecard"** disclaimer; the grill/ouroboros personas reliably
surface home-field bias and definitional sloppiness (e.g. CAI's two stages, RLHF's KL leash,
verifiability being task-conferred) that a single pass glosses over.
