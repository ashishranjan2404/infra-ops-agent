# J7 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "the parser is fragile"
**Problems found:**
- `_cre_excerpt` uses a regex on YAML instead of `yaml.safe_load`. A reordered or
  block-scalar-variant CRE could silently yield "". **Verdict:** acceptable — it is
  *best-effort context only*; the prompt still has service + log_marker, and scoring does
  not depend on the excerpt. But it must degrade to "" (not crash) on any CRE. → Confirmed:
  returns "" when no match.
- `prove_request_assembles` returns a Python truthiness on a mixed boolean expression
  (`... or "prompt" in payload`) — operator precedence could surprise. **Fix considered:**
  parenthesize. Current code: `bool(url) and isinstance(headers,dict) and "messages" in payload or "prompt" in payload`. Because `and` binds tighter than `or`, this is
  `(bool(url) and isinstance(...) and "messages" in payload) or ("prompt" in payload)`,
  which correctly accepts EITHER a chat payload (messages) OR a completion payload
  (prompt). Intentional and correct — documented here so it isn't "fixed" into a bug.

## Engineer B — "the eval is too easy / leaks"
**Problems found:**
- The gold fix appears verbatim in the menu and contains the service name, which also
  appears in the prompt. The lexical baseline can win by service-name overlap alone →
  inflates the floor. **Real gap.** Mitigation: report chance rate AND the baseline so the
  leakage is visible; the dry-run number (0.867) is explicitly the *baseline*, not the LLM.
  Free-form generation is named as the leak-free future version (needs a cluster).
- Ties in `baseline_policy` resolve to the first index (`>` not `>=`). Deterministic but
  arbitrary on ties. **Verdict:** fine for a reproducible baseline; documented.

## Engineer C — "the safety/blocked-step story is underspecified"
**Problems found:**
- A reader could run `--live-agent` and assume the kubectl command executed. **Fix
  applied:** every row carries `cloud_applied=false` + `cloud_blocked_reason`, and the
  top-level result has `cloud_executed=false`; the stderr summary prints `cloud_executed`.
- The runner doesn't *check* the blocker itself (it just records the reason string).
  **Verdict:** correct separation — the runner is cloud-free by construction; the blocker
  is verified once in 07_test_results.md with the real gcloud error, not re-run per row
  (which would risk touching cloud).
- `llm_policy` parses the first integer in the reply; a model that emits "step 1: ..."
  would misparse. **Real edge.** Verdict: acceptable for a 16-token answer-only prompt;
  recorded `raw` lets a human audit. The live minimax run surfaced exactly this class of
  issue (empty/garbled completions) — so the field earns its keep.

## Final filtered spec deltas
No code changes required; all three critiques are either (a) intentional and now
documented, or (b) honest caveats carried into 09_critique.md. The leakage caveat and the
"this is action-selection, not recovery" framing are the load-bearing disclosures.
