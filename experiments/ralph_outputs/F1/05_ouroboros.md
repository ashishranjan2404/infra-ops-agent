# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the citations are soft"
**Found problems:**
- CWM, SREGym, FIREBALL author/venue precision: claiming exact author lists risks being
  wrong post-cutoff. → **Fix:** attribute by team/known-author + year, hedge venue where
  unsure ("Meta FAIR CodeGen Team, 2025"; SREGym anchored to the arXiv id from
  PAPER_QUESTIONS). Describe by *mechanism* so the cite is defensible even if a venue
  detail is off.
- "AutoHarness" risks reading as a phantom paper. → **Fix:** explicitly frame it as a
  *paradigm* ("the AutoHarness line of work on automatically generating test harnesses")
  and anchor it to verifiable adjacent work (TestGen-LLM, search-based test gen).
- REx attribution. → **Fix:** describe REx by its mechanism (Thompson-tree over
  refinement candidates) which our `rex/tree.py` provably implements; keep the year
  conservative.

## Engineer B — "positioning gaps / over-claiming"
**Found problems:**
- Risk of implying C2 (transfer) is a *result*. The outline marks it *pending*. →
  **Fix:** §2.5 explicitly says "hypothesis under test, status pending the GRPO transfer
  branch." Don't claim transfer works.
- Constitutional-AI analogy could be overstated (we don't train a preference model). →
  **Fix:** state the three concrete differences (synthesized vs hand-written; hard code
  gate vs preference model; sim-grounded vs LLM-judged).
- Missing the *honest-gap* framing that differentiates us from pure self-refinement. →
  **Fix:** §2.4 surfaces the SME-vs-no-oracle ablation as what self-refine papers don't
  isolate.

## Engineer C — "validator under/over-engineered + structure"
**Found problems:**
- A pure token-presence check is weak — a token could appear in a wrong context. But a
  semantic check is impossible offline. → **Decision (accept the limit):** validator
  guarantees *coverage + structure* only; accuracy is a human guarantee via
  mechanism-based descriptions. Documented as a known limitation in 09_critique.
- The "balanced brackets" check could false-positive on legit prose using `[Author,
  Year]`. → **Fix:** make bracket balance a *soft* warning, not a failure.
- Need ≥6 subsections asserted so the section can't degenerate to one blob. → kept.

## Final filtered spec (deltas applied)
1. Mechanism-first descriptions; conservative venue/author; SREGym arXiv id grounded.
2. AutoHarness/REx as paradigm labels + real adjacent anchors.
3. C2 transfer flagged pending; Constitutional-AI analogy bounded by 3 explicit diffs.
4. Validator = coverage + structure; bracket balance is a soft warning. Limit documented.
