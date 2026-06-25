# 09 — Critique (honest)

## What a reviewer will attack
1. **Citation precision post-cutoff.** The strongest attack: an exact author/venue/year
   on a very recent work (CWM 2025, SREGym 2026, FIREBALL) could be slightly off. I
   mitigated by describing each work by its *stable mechanism* and hedging venue, but a
   camera-ready pass MUST verify every DOI against the actual papers. The validator
   cannot catch this (it checks presence, not correctness) — this is the section's
   biggest residual risk and is stated plainly.
2. **"AutoHarness" / "REx" as named citations.** These are the labels the *codebase*
   uses; if a reviewer cannot find a canonical paper under those exact titles, they may
   read them as phantom cites. I kept them as paradigm labels with real adjacent anchors
   (TestGen-LLM / search-based test gen for AutoHarness; bandit/Thompson refinement for
   REx), but the final paper should either (a) cite the specific REx paper the
   implementation was based on, or (b) demote both to "the X-style paradigm" with only
   the verifiable anchors. I could not resolve the exact REx provenance from the repo.
3. **Constitutional-AI analogy may be a stretch.** We don't train a preference model, so
   the analogy is structural, not literal. I bounded it with three explicit differences,
   but a skeptical reviewer might still cut the comparison. It is defensible but optional.
4. **Validator is shallow.** It verifies coverage + structure only — it cannot confirm a
   citation is *accurate* or *correctly positioned*. That is a human guarantee. I'm
   explicit that the script's job is anti-omission, not anti-error.

## What's weak / missing
- No bibliography/BibTeX entries with real URLs/DOIs — the section names works but does
  not yet provide a `references.bib`. A natural follow-up task (cf. the outline's
  "References (to fill)").
- C2 (FIREBALL transfer) is positioned as a *pending hypothesis*; if the GRPO transfer
  branch ultimately shows no transfer, §2.5 becomes a limitation rather than related
  work and would need re-framing.
- Some adjacent works a picky reviewer might expect are omitted for length (process vs
  outcome reward models; ReAct; Toolformer). Defensible scoping, but worth noting.

## Honest status
Deliverable is **complete and validated**, but its quality ceiling is *citation
accuracy*, which is exactly what an offline doc task cannot fully self-verify. The
content/positioning is solid and repo-grounded; the open risk is bibliographic precision,
flagged for a camera-ready verification pass.
