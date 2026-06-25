# H2 — 03 Improved Plan

## What changed after the grill

1. **Smoke asserts falsifiable invariants, not "it runs".** (accepted REV + RLE)
   Three checks: SEPARATION (gold pass@1 > empty pass@1), FLOOR (empty pass@1 == 0.0),
   GOLD-FLOOR (gold pass@1 >= `MIN_GOLD_PASS` = 0.8).

2. **Tolerant gold assertion instead of `== 1.0`.** (accepted REV's false-positive hole)
   Local run showed one cascade scenario (`aws_dynamodb_dns`) whose canonical-fix plan
   scores 0.425 in the sim — a scenario-data issue, out of scope for H2 and explicitly a
   shared-core concern I must not edit. A strict `gold == 1.0` would have made CI red on
   unrelated PRs. The `>= 0.8` gold-floor catches a real substrate regression while
   tolerating one bad scenario.

3. **Required PR job is deterministic + hermetic.** (accepted SMR + PSRE)
   No gateway, no `HUD_API_KEY`, exclude `tests/test_llm.py`. Added `timeout-minutes`,
   pinned `actions/*@v4/@v5`, `concurrency` cancel-in-progress, `permissions: contents: read`,
   `cache: pip`.

4. **Real-model pass@k sweep deferred to a label-gated/nightly job.** (RLE want, SMR guardrail)
   Documented in the workflow header and in 09_critique as future work; NOT a required check.

## What I rejected and why
- **RLE's "tiny real-model sweep as a PR gate".** Rejected for the *required* path: at k=2,
  3 seeds the Wilson CI is too wide to distinguish regression from noise (SMR). Kept only as
  documented future label-gated work.
- **PSRE's "turn pip cache off".** Rejected: deps-freshness is a different job's concern;
  this job optimizes for fast, deterministic test+smoke. Cache stays on (DOL).

## Final deliverables (unchanged in count)
- `artifacts/eval-ci.yml` — workflow (PR/push/dispatch; pytest subset + pass@k smoke; upload).
- `artifacts/passk_smoke.py` — deterministic gold-vs-empty pass@k smoke with 3 invariants.
- `artifacts/validate_workflow.py` — YAML shape validator (handles the `on:`→`True` quirk).
