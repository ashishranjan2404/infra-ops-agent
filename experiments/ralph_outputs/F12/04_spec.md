# F12 — 04 Spec

## Deliverable 1: `artifacts/SRE_Degrees_2pager.md`

Format: Markdown, single doc, ~1,100–1,400 words (≈2 printed pages). Section contract:

| # | Section | Must contain | Word budget |
|---|---------|--------------|-------------|
| H | Title + one-line hook | product in one sentence | ~30 |
| 1 | The Problem | incidents cost money; humans are the bottleneck; the trap (loudest alert ≠ root cause; naive fix worsens it) | ~180 |
| 2 | Why Now | frontier models exist but fail real cascades on the first try | ~120 |
| 3 | The Insight (graduation / code-as-policy) | model stays FROZEN; the code scaffold around it gets smarter; grade root-cause+fix+trap, not "did it come back up" | ~180 |
| 4 | The Evidence | headline: pass@1 0.23 → 0.90; two models agree; honest negative | ~200 |
| 5 | The Product / Wedge | eval + training-data engine ("SAT + practice problems for incident AI"); expansion = autonomous responder | ~160 |
| 6 | Market | who pays, directional TAM, clearly labeled as estimate | ~140 |
| 7 | Moat | proprietary cascade catalog + root-cause-aware grader + graduation loop | ~110 |
| 8 | The Ask | raise size placeholder, use of funds, milestone | ~90 |
| F | Footnote | rigor: n, seeds, models, judge, CIs, McNemar p | ~40 |

### Hard constraints (test cases)
- T1: total words in [1100, 1400].
- T2: contains all 5 required topics (problem, insight, evidence, market, ask) — grep for anchors.
- T3: contains the exact headline pair 0.23 and 0.90 (from A1).
- T4: contains the second-model corroboration 0.893 / 0.240 (from A2).
- T5: contains the honest negative (rex_no_oracle / "where the lift comes from").
- T6: footnote contains n, seeds, "McNemar", and "deterministic".
- T7: no undefined jargon — "pass@k", "Thompson", "FIREBALL", "MCTS" either removed or defined
      inline in plain English.
- T8: markdown parses (no broken headings/tables).

## Deliverable 2: `artifacts/evidence_check.md`
A table: Claim (as it appears in the memo) | Number | Source file | Source line/field.
Every quantitative claim in the memo must have a row. Plus a "labeled estimate" list for any
market/TAM figure that is directional rather than measured.

## Numbers that are ALLOWED (traceable to A1/A2 only)
- A1: zero_shot pass@1 0.230 [0.17,0.31]; rex pass@1 0.897≈0.90 [0.83,0.94]; 42 incidents
  (12 simple/20 cascade/10 novel); 5 conditions; 3 seeds; 630 episodes; 0 errors; ~27 min;
  glm-5p2; deterministic P0 judge; per-family rex: simple .889 / cascade .850 / novel 1.000.
- A2: deepseek-v4-pro; rex pass@1 0.893 [0.83,0.93] vs zero_shot 0.240; 750 episodes; 0 errors;
  ~45 min; McNemar p<0.0001; rex_no_oracle 0.287 ≈ best_of_n 0.307.
- Architecture: reward = 0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap; frozen LLM;
  two-tier (in-process sim + live GKE); 5 frontier models across 4 providers.

## Numbers that are FORBIDDEN
Any revenue, customer count, pipeline, LOI, or precise TAM not labeled as an estimate.
