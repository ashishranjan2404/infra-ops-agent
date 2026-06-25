# 04 — Spec

## Deliverable A: `artifacts/why_were_different.md`
A single-page Markdown document. Constraints:
- Length: fits on one printed page (~550–750 words, scannable).
- Sections, in order: Title + one-line thesis; "The wedge"; "The moat"; "Proof points (real
  runs)"; "What we do NOT claim"; "The ask".
- Tone: honest, punchy, declarative. No hedging filler. Every number followed by a source tag
  like `[src: docs/headline_insights.md]`.
- No invented numbers. Only numbers present in `proof_points.json`.

### Content contract (the load-bearing claims)
| id | claim | value | source |
|----|-------|-------|--------|
| C1 | reconstructed real post-mortems | 19 | `opensre-traj/specs/real/*.json` |
| C2 | generated scenarios | 51 | `scenarios/cidg/generated/*.yaml` |
| C3 | reward formula | `0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap` | `ARCHITECTURE.md` / `rex/scoring.py` |
| C4 | within-group reward spread | 0.0 / 0.15 / 1.0 | `ARCHITECTURE.md` |
| C5 | verifier generalization | 0.90 held-out acc vs 0.95 hand-written; 14→3 rules; 3 unseen incidents | `docs/headline_insights.md` |
| C6 | weak/strong separation, one-shot | haiku 0.27 vs opus 0.50 mean | `docs/headline_insights.md` |
| C7 | small+REx > big zero-shot (easy tier) | haiku+REx 0.86 > opus zero-shot 0.81 | `ARCHITECTURE.md` |
| C8 | hard-tier honesty | zero-shot 0.19–0.42; REx ~triples + escalates unsolvable | `ARCHITECTURE.md` |
| C9 | honest ablation caveat | REx lift mostly oracle leakage; stripped → 0.25 ≈ zero-shot 0.24 | `docs/headline_insights.md` |
| C10 | model/provider breadth | 5 frontier models, 4 providers, one HUD key → 200+ models | `ARCHITECTURE.md` |
| C11 | two-tier fidelity | in-proc sim + live GKE call-mesh, alert fires on victim | `ARCHITECTURE.md` |
| C12 | reproducibility | `python3 -m rex.frontier` | `ARCHITECTURE.md` |

## Deliverable B: `artifacts/proof_points.json`
Schema:
```json
{
  "task_id": "G8",
  "generated": "<ISO date>",
  "claims": [
    {"id":"C1","claim":"<text>","value":"<string|number>","source":"<repo path>","verified":true|false}
  ]
}
```
- MUST be valid JSON (validated with `python3 -m json.tool`).
- `verified` = true only if the source path exists OR the number was read directly from a file
  in this session. Counts (C1=19, C2=51) verified by `ls | wc -l` in step 06/07.

## Validation / test cases (step 07)
- T1: `proof_points.json` parses (`json.tool`).
- T2: `why_were_different.md` exists, is one page (word count < 800), contains all section headers.
- T3: C1 count check: `ls opensre-traj/specs/real/*.json | wc -l == 19`.
- T4: C2 count check: `ls scenarios/cidg/generated/*.yaml | wc -l == 51`.
- T5: every `[src: …]` path in the one-pager that points at a repo file exists.
