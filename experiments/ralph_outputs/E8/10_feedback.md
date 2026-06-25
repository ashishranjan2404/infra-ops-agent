# E8 — 10 Feedback for the next task

The Fireball-data blocker is real and recurring (see also P7): the repo holds only ~319
Fireball-format trajectories in `opensre-traj/out/trajectories.jsonl` and NO
fireball-trained model slug — so any task asking for a *trained* scaling/transfer result
must be scoped as "harness + power analysis + documented blocker," never a fabricated
curve. The highest-leverage move when a task's headline quantity is blocked is to (a) make
the harness *degrade honestly* — cap at corpus size, expose requested_N vs actual_N, set
`blocked:true`, emit no scores — and (b) compute the adjacent quantity you *can* (here, the
eval-rollout N from a closed-form power analysis with the observed reward sd ≈ 0.22). Two
reusable seams emerged that the next worker should exploit: the `FitCallback =
(list[Record], str) -> float` signature lets a future PR inject a real trainer/evaluator
without touching the harness, and the stratified+nested subsetter is corpus-agnostic
(works on any JSONL with id/family/trajectory keys), so it can drive sweeps for other
datasets too. Keep anti-fabrication gates as tested code, not prose — the `<4 points → None`
and `no fit → blocked` tests are what make "we didn't fake it" verifiable.
