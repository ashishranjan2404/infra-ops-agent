# D5 — 05_ouroboros (self-critique as 3 different engineers)

## Engineer A — Data Integrity
**Problems found.**
- A1. The prompt reconstruction depends on `import hud_env`, which imports `from hud import
  Environment`. If `hud` isn't installed in the offline (3.13) env, the data builder crashes at
  import — defeating "runs offline." **Fix:** the builder must reconstruct the prompt WITHOUT
  importing the HUD env module. Read scenario specs directly, or — simpler and sufficient for SFT
  targets — store the *answer* as the completion and a lightweight prompt key, and only fully render
  the prompt when the HUD env is present. For the offline deliverable, the completion (the demo
  answer) is the load-bearing part; a prompt stub keyed by scenario_id is acceptable and documented.
- A2. "best per scenario" ties: two demos with equal max reward → nondeterministic pick. **Fix:**
  tie-break by `(reward, model, trace_id)` so it's stable.
- A3. Eval scenarios with NO trajectory at all can't be graded offline. **Fix:** the offline proxy
  only iterates scenarios that HAVE ≥1 demo; report skipped.

## Engineer B — Experimental Validity
**Problems found.**
- B1. The pool mixes three demonstrator models. "Best per scenario" silently selects whichever model
  happened to win — so the SFT target distribution is a Frankenstein of three policies, not one
  coherent teacher. That's defensible (RAFT does this) but must be *reported* (per-scenario teacher
  model histogram), or a reviewer assumes a single teacher.
- B2. The offline proxy grades the *same answers* it selected as best — circular: it will look
  near-ceiling by construction for SFT and tells us nothing about generalization. **Fix:** the
  proxy must grade demos on the EVAL split (held out from SFT-target selection), and the report must
  state plainly that this is an *upper bound on what cloning these demos could achieve*, not the
  trained result. Re-label the offline number `proxy_ceiling` everywhere.
- B3. Reward in the pool was computed by an earlier grader version (possibly hud_env, not v2). Mixing
  pooled `reward` with a freshly-computed v2 score is an apples/oranges risk. **Fix:** recompute the
  comparison metric uniformly with one grader path in the harness; treat pooled `reward` only as the
  *selection* signal for best-demo, and say so.

## Engineer C — Operational / Over-under-engineering
**Problems found.**
- C1. `train_sft.py` writing a real Tinker loop is *over-engineering* if the SDK doesn't support
  supervised targets — we'd be guessing the API. **Fix:** make train_sft.py a thin, honest scaffold:
  it loads data, builds batches, and at the training call it introspects `TrainingClient` for a
  supervised method; if absent it raises `NotImplementedError` naming the missing API. Better an
  honest stub than a plausible-looking fake.
- C2. The hack-diagnostic token count uses `len(answer)/100` — char-based, not tokens; fine as a
  coarse density but label units honestly (per-100-chars).
- C3. Two YAML configs that 90% overlap invite drift. **Fix:** factor shared keys (`split_path`,
  `base_model`, `grader`, `eval_metric`) and only differ on the regime block. Keep them as two files
  (the brief wants a config for both) but mirror the shared keys exactly and assert equality in T5.

## Final filtered spec (deltas applied)
- Builder is import-light: does NOT import `hud_env`; stores `prompt_ref` (scenario_id) + completion;
  full prompt rendered only when HUD present. Tie-break stable. (A1, A2)
- Offline harness grades EVAL-split demos only, output named `proxy_ceiling`, with explicit
  "upper bound, not trained result" caption; recomputes metric with one grader path. (B2, B3)
- Teacher-model histogram reported. (B1)
- train_sft.py is an honest scaffold that introspects the SDK and raises a precise NotImplementedError
  if supervised step is unavailable. (C1)
- Hack density labeled per-100-chars. (C2) Configs share keys verbatim, asserted in tests. (C3)
