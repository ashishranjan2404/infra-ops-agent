# I6 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Filter widened from "0-reward" to the full failure tail** (`score < 1.0` OR
   `failed_checks ≠ ∅`), because the reward is graded and exact-0 is degenerate.
   The strict `score == 0.0` subset is still reported as its own line. *(accepted SMR)*
2. **`trap_taken` is the top precedence label** for the primary bucket. *(accepted PSRE)*
3. **Every figure is reported as `k of n`** with the corpus name; no bare percentages.
   A `caveat` field in the JSON states small-N. *(accepted AR)*
4. **Added a ground-truth fixture**: re-derive `failed_checks` for a tuple whose answer
   the probe file already stores, assert equality. This validates the HUD re-scoring
   path. *(accepted RLE)*
5. **Added a `safe_abstain` secondary tag**: a rollout with an empty action plan that
   avoided all traps is tagged so PSRE's "graceful degradation is not a real failure"
   distinction is visible in the data, even though it still appears in the tail.
   *(partially accepted PSRE — tagged, not excluded)*

## Rejected / deferred
- **AR's "don't report percentages at all":** REJECTED. Percentages are fine *with n
  attached*; enumerating the failure surface is the goal (RLE). We keep both counts and
  rates, gated by the caveat.
- **Full statistical CI per bucket:** DEFERRED. N is too small to be meaningful; a
  Wilson interval on n=12 is theater. Out of scope.

## Final approach
Two ingest paths → one unified `Rollout` record → one bucketer → one report.
- Path A (probe jsonl): rows already carry `score`/`failed_checks` → ingest directly,
  also recompute to self-check.
- Path B (HUD traces): pull `rex.score_plan` request payloads, build a `_Scenario`
  shim, replay `rex.scoring.score_plan` + `failed_checks` deterministically.
Dedup HUD by `(trace_id)` since propose/run/score share a trace.
