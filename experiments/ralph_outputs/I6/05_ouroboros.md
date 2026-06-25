# I6 — 05 Ouroboros (self-critique, 3 engineers)

## Engineer A — correctness of the re-scoring path
**Problem found:** The captured HUD `scenario` payload may not expose `category`, and
`build_judge_prompt` reads `getattr(scenario, "category", "unknown")`. In deterministic
mode the category is irrelevant (keyword judge), but if `JUDGE_MODE` is ever `llm`/`hybrid`
the shim would silently mis-judge. **Fix:** force deterministic mode explicitly inside the
script (`os.environ["REX_JUDGE_MODE"]="deterministic"` before importing rex.scoring, and
pass `judge_fn=rex.scoring.deterministic_judge` so it's hermetic regardless of env).

**Problem found:** `failed_checks` reads `sim_result.get("applied_actions", plan.actions)`.
If a HUD `sim_result` has `applied_actions: []` (blocked) but the plan had a trap, the trap
is NOT counted (because the sim blocked it). That is actually CORRECT behavior — a blocked
trap is not a taken trap — but it means our `trap_taken` bucket = *successfully executed*
traps, not *attempted* traps. **Fix:** add an `attempted_trap` secondary tag computed from
`plan.actions` directly, so attempted-but-blocked traps are still visible.

## Engineer B — taxonomy completeness / "timeout" bucket
**Problem found:** The task text names `timeout` as an example bucket, but the REx data has
no wall-clock timeout concept — a rollout either produces a plan or an empty plan. Claiming
a `timeout` bucket with always-0 would be misleading. **Fix:** Do NOT invent a timeout
bucket. Document explicitly that REx rollouts are single-shot plan submissions with no
timeout dimension; the nearest analog is `empty_plan` (model abstained / produced nothing).
State this in the report so a reader doesn't expect timeouts.

**Problem found:** `not_resolved` will co-occur with almost every other failure (if you
didn't fix it, it's not resolved). As a *primary* bucket it'll be near-empty (only the rare
"right fix but sim still unresolved" case). **Decision:** keep precedence as-is — that
near-empty `not_resolved` count is itself informative (it isolates fix-applied-but-failed).

## Engineer C — reporting honesty & reuse
**Problem found:** Reporting `primary_bucket_pct` over a ~60-rollout corpus invites
over-reading. **Fix:** keep pct but pin a `caveat` and always show the `k of n` count
alongside in the markdown.

**Problem found:** Duplicate episodes — the same scenario re-run across many HUD trace
files would double-count. **Fix:** dedup HUD rollouts by `(scenario, root_cause_text,
tuple(actions))` so identical re-emissions collapse; keep distinct refinement iterations.

## Final filtered spec deltas
- Force deterministic judge in-script + inject `deterministic_judge`.
- Add `attempted_trap` tag (from raw plan) distinct from executed `trap_taken`.
- No `timeout` bucket; document the single-shot nature + map abstain→`empty_plan`.
- Dedup HUD by (scenario, root_cause, actions).
- pct retained but always paired with counts + caveat.
