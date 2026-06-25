# F12 — 01 Plan

## Objective
Write a crisp, honest, 2-page non-academic summary of the SRE-Degrees project for a
YC / fundraising audience. It must cover: the problem (SRE autonomy), the insight
(graduation / code-as-policy), the evidence (REAL numbers from A1/A2), the market, and the ask.
Punchy, no jargon, no hype-padding.

## Approach
1. Mine the real evidence: A1 (full 42-incident pass@k on glm-5p2) and A2 (750-episode
   ablation on deepseek-v4-pro, McNemar significance). Use ONLY numbers that exist in those
   `result.json` / `SUMMARY.md` files. No invented metrics.
2. Mine the framing: `ARCHITECTURE.md` (code-as-policy, frozen LLM, root-cause-aware reward,
   two-tier sim + live GKE) and the memory note (graduation = evolve code around a frozen model,
   not fine-tune weights).
3. Draft a 2-page memo with a fundraiser's structure: hook → problem → why-now → insight →
   proof → market → moat → ask. Translate every technical term to plain English.
4. Keep the honest negatives in (rex_no_oracle ≈ baseline). Investors trust founders who
   name their own weak spot.
5. Validate: word count fits ~2 pages (~1,100–1,400 words), every quantitative claim is
   traceable to an artifact, no jargon left unexplained.

## Files to create
- `artifacts/SRE_Degrees_2pager.md` — the deliverable (the 2-page memo).
- `artifacts/evidence_check.md` — a claim→source table proving every number is real.
- The 10 Ralph step files + SUMMARY.md + result.json.

## Files to MODIFY
- None. This is a writing task. No shared core file touched (rex/*, sim/*, agent/*, experiments/*.py).

## Dependencies
- A1/A2 outputs (read-only). ARCHITECTURE.md (read-only). Memory note (read-only).

## Risks
- R1: Inventing numbers. Mitigation: evidence_check.md cross-references every stat.
- R2: Jargon creep ("pass@k", "Thompson sampling", "FIREBALL schema"). Mitigation: a
  jargon-scrub pass; define or delete each term.
- R3: Over-claiming ("solves SRE"). Mitigation: scope claims to what A1/A2 actually show, and
  keep the honest caveat in the memo.
- R4: Market section becoming fiction. Mitigation: use directional, sourced-or-clearly-estimated
  TAM framing and label estimates AS estimates.

## Success criteria
1. ~2 pages (1,100–1,400 words), readable by a non-technical investor.
2. Contains the 5 required sections: problem, insight, evidence, market, ask.
3. Every quantitative claim traces to an A1/A2 artifact (evidence_check.md proves it).
4. Honest: at least one named limitation; no fabricated traction.
5. Markdown parses clean.
