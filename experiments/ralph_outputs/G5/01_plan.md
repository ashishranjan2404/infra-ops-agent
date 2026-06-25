# G5 — 01 Plan

## Objective
Produce a real, honest, sourced **positioning matrix** comparing our project (SRE-Degrees /
REx code-as-policy harness) against three named reference points:
- **SREGym** (academic live benchmark for AI SRE agents, arXiv 2605.07161)
- **Komodor** (commercial autonomous AI SRE / Kubernetes platform — "Klaudia")
- **Datadog Bits AI SRE** (commercial autonomous SRE agent inside Datadog)

across five comparison dimensions:
1. Open benchmark (is the substrate public/reproducible?)
2. Trap-action safety (does the system explicitly grade/penalise the *harmful* action?)
3. Training method (does it produce training signal, fine-tune, or just orchestrate a frozen LLM?)
4. Deployment posture (research harness vs. SaaS attached to live prod)
5. Evaluation rigor (root-cause-aware grading vs. "did it come back up"; independence of eval)

## Approach
- Pull our own positioning from `ARCHITECTURE.md` (the reward, the trap penalty, frozen-policy
  stance, the curriculum, the 0.86 ceiling = "escalate the unsolvable").
- Source each competitor claim from primary material (arXiv abstract, vendor blogs, press
  releases) gathered via web search. Mark every cell with a citation tag and flag where a claim
  is **vendor-stated and not independently verified**.
- Build a markdown table + per-cell prose, plus a "where we are honestly weaker" section (we are
  a research harness, not a deployed product; we have no real customers, no scale data).

## Files to create
- `01..10` step files + `SUMMARY.md` + `result.json`
- `artifacts/positioning_matrix.md` — the primary deliverable (matrix + sourced claims + sources)
- `artifacts/sources.json` — machine-readable source list (url, who, claim, verification status)
- `artifacts/validate_matrix.py` — a tiny validator that parses the matrix table and checks every
  cell carries a citation tag + every tag resolves to a source in sources.json

## Dependencies
- Web (search) — used at authoring time only; deliverable is static markdown/JSON, no live deps.
- Python 3 stdlib (`re`, `json`) for the validator. No external packages.

## Risks
- **Overclaiming vs. competitors** — biggest risk; honesty is the deliverable's whole value.
  Mitigation: every competitor cell cites a primary source and flags "vendor-stated".
- **Apples-to-oranges** — we are a *benchmark/data generator*; Komodor & Datadog are *products*;
  SREGym is a *benchmark*. The matrix must say so up front, not pretend they're the same category.
- **Staleness** — vendor features move fast (Komodor self-healing GA Nov 2025; Bits "deeper
  reasoning" Mar 2026). Mitigation: date-stamp every competitor claim.

## Success criteria
- Markdown table with 4 columns (us + 3) × 5 dimensions, every cell populated.
- Every competitor claim sourced to a real URL; vendor marketing flagged as such.
- An explicit "honest weaknesses of our position" subsection.
- `validate_matrix.py` runs clean: every cell tagged, every tag resolves.
