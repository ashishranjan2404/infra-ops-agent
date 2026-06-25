# F5 — Plan: Tighten the Abstract to ≤250 words for AAAI

## Objective
The PAPER_OUTLINE.md ships a ~230-word abstract draft (lines 9–27) that is currently
loose: it over-claims in places ("large, statistically significant lift") relative to
what the real result JSONs support, and it is written for a self-audience. Deliver a
**tight, ≤250-word abstract** for AAAI that (a) reflects the *actual* contributions and
(b) reports *honest* results grounded in `docs/headline_insights.md` and the run JSONs,
not the aspirational outline numbers. Count the words and report the count.

## Approach
1. Read the canonical sources of truth:
   - `experiments/PAPER_OUTLINE.md` — claims C1/C2/C3, contributions list, framing.
   - `docs/headline_insights.md` — the *honest* numbers actually measured.
   - `rex/runs/harness_synth.json`, `rex/runs/ablation.json` — raw evidence.
2. Reconcile the outline's optimistic phrasing against the honest insights. Where they
   disagree, prefer the honest insight (this is the AAAI-reviewer-safe choice).
3. Draft an abstract structured as: problem (MTTR/cascades) → gap (LLMs hit trap
   actions) → method (3 composable components) → results (with real numbers) → honest
   limitation → artifacts released.
4. Enforce ≤250 words with a real word count (`wc -w` on the abstract body).
5. Deliver `abstract.md` as the task artifact.

## Files to create
- `experiments/ralph_outputs/F5/artifacts/abstract.md` — the deliverable.
- The 10 step files + SUMMARY.md + result.json under `experiments/ralph_outputs/F5/`.

## Files I must NOT touch (shared core)
- `experiments/PAPER_OUTLINE.md` (shared doc — propose, don't edit).
- `rex/*.py`, `sim/*.py`, `agent/*.py`, `ralph_status.json`.

## Dependencies
- None external. Pure writing + a `wc -w` word count. No cluster, no API, no GPU.

## Risks
- **Number drift**: the outline cites 89.7%/94.9% verifier accuracy and "≥2× pass@1";
  the honest insights cite 0.90 vs 0.95 and oracle-leakage collapse. Risk of citing a
  number the data doesn't back. Mitigation: cite only what the JSONs/insights support;
  hedge the rest.
- **Word-count creep**: abstracts balloon. Mitigation: hard `wc -w` gate, iterate down.
- **Over-claiming the refinement loop**: the ablation shows REx's lift was largely
  oracle-feedback leakage. The abstract must NOT sell the loop as the headline; the
  defensible contributions are the verifiable env + searched verifier.

## Success criteria
- `abstract.md` exists, is valid Markdown, body ≤250 words (counted, reported).
- Every quantitative claim traces to a real artifact (insight doc or run JSON).
- It states at least one honest limitation (novel-incident gap / oracle leakage / flat RLVR).
- It names the released artifacts (harness, simulator, benchmark, deterministic reward).
