# 01 — Plan (G8: "Why We're Different" one-pager)

## Objective
Produce a crisp, honest, punchy one-pager for investors/partners that synthesizes the
competitive analysis (G5/G6/G7) into: **the wedge**, **the moat**, and **proof points from
real results**. The thesis: an *open graduation benchmark* for autonomous incident response
plus *trap-action safety* grading is what we have that incumbents do not.

## Approach
G5/G6/G7 directories exist but are still empty (parallel workers in flight), so I synthesize
the competitive frame directly from the repo's real, verified assets rather than fabricating
upstream outputs. Sources of truth:
- `ARCHITECTURE.md` — thesis, the reward formula, the REx frontier table (5 models, 4 providers).
- `docs/headline_insights.md` — the 4 headline results **including the honest ablation caveat**.
- `docs/ENVIRONMENT_DESIGN.md` — the fidelity bar (cascading, misleading symptom, naive-fix-worsens).
- `opensre-traj/specs/real/*.json` — 19 reconstructed real post-mortems (AWS, Cloudflare, GitHub, Slack…).
- `scenarios/cidg/generated/*.yaml` — 51 generated scenarios.

## Files to create
- `experiments/ralph_outputs/G8/01..10` + `SUMMARY.md` + `result.json`
- `experiments/ralph_outputs/G8/artifacts/why_were_different.md` — the deliverable one-pager.
- `experiments/ralph_outputs/G8/artifacts/proof_points.json` — machine-checkable table of the
  numeric claims with their source files (so the one-pager is auditable, not vibes).

## Dependencies
None runtime. This is a synthesis/writing task over existing verified artifacts. No core file edits.

## Risks
- **Overclaiming.** The honest ablation (insight #3) shows REx's *headline lift* was largely
  oracle-feedback leakage. A dishonest one-pager would hide this; an honest one *leads with the
  defensible claim* (the verifiable environment + the searched verifier) and is upfront about
  what REx alone does not buy. This is the single most important constraint.
- **G5/G6/G7 empty** → I cannot quote their exact framing. Mitigation: ground every claim in a
  repo artifact path; note the dependency in `07`/`09`.
- **Audience mismatch.** Investors want the wedge + moat + traction; engineers want rigor.
  One page must do both → lead with the wedge, back each line with a cited number.

## Success criteria
1. One page, scannable (wedge / moat / proof / honest-caveat / ask).
2. Every numeric claim traceable to a real file in the repo (proof_points.json validates).
3. Honest: includes the ablation caveat, not just the flattering numbers.
4. `proof_points.json` parses as valid JSON; one-pager parses as valid Markdown.
