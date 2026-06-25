# I6 — 10 Feedback for the next task

The highest-leverage move was realizing the HUD traces don't store the reward but DO store
the full `{plan, scenario, sim_result}` request payload — so a deterministic scorer can be
*replayed* over captured episodes to reconstruct per-rollout signals. Any future task that
needs per-rollout rewards/labels should mine `rex/runs/hud/*.jsonl` the same way (filter
`name=="rex.score_plan"`, read `hud.request` payload, inject `deterministic_judge` for
hermetic re-scoring) rather than assuming the reward is missing. Two data-shape gotchas to
carry forward: (1) probe jsonl rows store score/failed_checks but NOT the action plan, so
plan-derived tags must default to "unknown" not 0; (2) the failure distribution is heavily
scenario-imbalanced (one scenario dominated 56% of failures), so always report by-scenario
counts alongside any headline rate. Finally, importlib-loaded modules with `@dataclass`
need `sys.modules[name]=mod` set before `exec_module`, or dataclass construction throws.
The deepest finding worth chasing: the reward penalizes *correct safe abstention* on
unfixable scenarios (singleton node) as `no_fix` — a reward-design issue, not a model error.
