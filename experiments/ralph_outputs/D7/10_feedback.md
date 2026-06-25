# D7 — 10 Feedback for the next task

The biggest lesson: in this frozen-LLM / code-as-policy repo, "train on family X"
**must be reframed as "exemplar pool = family X"** — there are no gradient steps in the
local loop, so any task phrased as training is really a data-mix / in-context ablation,
and the deliverable should say so loudly to avoid a "this isn't training" reject. Second:
**check for saturation before spending budget** — glm-5p2 sits at ceiling on `simple`
and floor on `cascade`, so transfer effects are invisible no matter how clean the
harness is; a quick zero-shot probe per family up front tells you whether the chosen
model can even show the effect, and if it's saturated, pick a mid-difficulty model or
harder/easier incidents *first*. Third, reuse pays off: `scenarios_by_family`,
`run_plan`+`score_plan` (deterministic judge), and `compute_pass_at_k` (Wilson CI) let
the whole experiment be an additive wrapper with **zero core edits** — the only friction
was `symptom`/`gold_root` having no public accessor (had to read `_SCENARIOS` privately;
a tiny public getter in core would help future tasks). Finally, the two-tier
`--dry-run` (zero-network wiring + leakage assertion) then reduced real run pattern is
the right way to respect a 15-min cap while still proving the live path — budget the
real run at ~5s/LLM-call and keep episodes ≤ ~24 for headroom.
