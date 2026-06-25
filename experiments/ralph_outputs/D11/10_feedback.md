# D11 — Feedback for the next task

The biggest lever was checking the trainer's CLI args and grepping logs for a `seed` field
*before* planning — that one check (no `--seed` anywhere) reframed the whole task from
"compute the CI" to "the CI is structurally blocked; build the harness that unblocks it +
report the variance that DOES exist." For any "measure X variance/stability" task on this
repo, first confirm the controlled variable is even controllable in the code; opensre's
RFT logs (`opensre-traj/runs/*.jsonl`) record per-step `mean_reward`, per-step `rewards[]`,
and (v2 only) `reward_std`, but `loss` is always null and there is no seed/run-id, so seed
and loss variance are both unavailable from existing data. Keep analyzers stdlib-only and
decoupled from HUD/the trainer so they run in the offline worker, and watch the
`importlib.util` + `@dataclass` gotcha (register the module in `sys.modules` before
`exec_module`). Generate patches mechanically (modify a temp copy, `git diff`, fix the
`---/+++` headers) and verify with `git apply --check` rather than hand-writing `@@` hunks,
which git rejects.
