# F5 — Spec: the abstract deliverable

## File format
- Path: `experiments/ralph_outputs/F5/artifacts/abstract.md`
- Format: GitHub-flavored Markdown.
- Structure:
  - `# Abstract` heading (NOT counted in the 250).
  - One single paragraph of abstract prose (the COUNTED body).
  - A `---` rule.
  - A `**Word count: N**` line (NOT counted).
  - A `## Provenance` section mapping each quantitative claim → source artifact
    (NOT counted; this is the audit trail, not the abstract itself).

## Word-count contract
- Define "the abstract" = the prose paragraph only, between the `# Abstract` heading and
  the `---` rule.
- Counting method: `sed -n '/^# Abstract/,/^---/p' abstract.md | grep -v '^#' | grep -v '^---' | wc -w`
  → must be ≤ 250.
- Report the integer count in `07_test_results.md` and in the `**Word count: N**` line.

## Content contract (every claim must be source-backed)
| Claim in abstract | Allowed phrasing | Source artifact |
|---|---|---|
| MTTR > detection; cascades are the hard case | qualitative | PAPER_OUTLINE.md §1 |
| naive fix worsens the outage | qualitative | PAPER_OUTLINE.md §1 (CoreDNS/InnoDB/NLB) |
| synthesized harness, Thompson search, rules-as-data | qualitative | PAPER_OUTLINE.md §3.2; `rex/harness_synth.py` |
| verifier generalizes ~0.90 vs ~0.95 hand-written | approximate, no 2-dp | `headline_insights.md` §2; `harness_synth.json` |
| 14→3 rule compression; one miss = unseen hazard | exact 14→3 | `headline_insights.md` §2 |
| deterministic verifiable reward, no LLM judge, credit-free | qualitative | PAPER_OUTLINE.md §3.4; insights theme |
| REx lift is SME-feedback-dependent; stripped → ≈ zero-shot | qualitative + the ≈ equality | `headline_insights.md` §3; `ablation.json` |
| 42-incident family-labeled benchmark from 19 postmortems | exact counts | PAPER_OUTLINE.md §4 |
| released artifacts | list | PAPER_OUTLINE.md abstract/contributions |

## Forbidden (would be unsupported by repo artifacts)
- No two-decimal verifier accuracies (n=3 held-out → false precision).
- No asserted McNemar p-value (grid partly pending in outline §5).
- No C2/FIREBALL transfer stated as a *measured* result (pending, outline §5.3).
- No "≥2× pass@1" as a locked claim (insights §3 shows the lift is leakage-dependent).

## Validation / test cases
- T1: file exists and is non-empty.
- T2: body word count ≤ 250 (the hard gate).
- T3: body word count ≥ 180 (a too-short abstract under-specifies the contributions).
- T4: contains the trap-action hook (regex `naive fix` or `worsen`).
- T5: contains the honest limitation (regex `feedback` AND (`zero[- ]shot` OR `collapse`)).
- T6: contains released-artifacts mention (regex `releas` AND `benchmark`).
- T7: markdown parses (heading present, single `---` rule present).
