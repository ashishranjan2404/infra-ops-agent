# E10 — Feedback for the next task

Writing tasks whose *subject matter* is empirically blocked are very doable and worth doing:
the right move is a **pre-registered protocol** with explicit `PENDING` cells and a stated
falsification criterion, not a stalled "blocked" punt. Two things made this clean and fast:
(1) the E3–E9 experiment designs already existed verbatim in `experiments/NEXT_100_TASKS.md`
and the blocker was already diagnosed in `experiments/results/P7_fireball_status.md` — so
*always grep the experiments/ dir for prior status notes before assuming you must invent the
design*; and (2) a tiny scoped validator that distinguishes legitimate prose decimals (reward
weights, dataset sizes) from forbidden result-cell numbers turned "don't fabricate" from a
promise into an enforced invariant — future writing tasks should ship a similar 30-line gate.
The one trap to flag downstream: this project's spine is *frozen-LLM / code-as-policy*, but
the transfer contribution (C2) is the single place it fine-tunes — any section touching C2
must explicitly reconcile that tension or a reviewer reads it as a contradiction.
