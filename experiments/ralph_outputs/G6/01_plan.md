# G6 — 01 Plan

## Task
Analyze Datadog's **Bits AI SRE** public material: what do they claim, what can't they (publicly) do, and how does *our* graduation/root-cause-aware framework (SRE-Degrees) differentiate. Be fair and sourced.

## Objective
A sourced, defensible analysis doc (not marketing rebuttal) that:
1. Faithfully summarizes Datadog's stated capabilities, with citations to **primary** sources (Datadog blog/docs/press) plus one independent source.
2. Identifies the **gaps/limits** — split into (a) explicitly acknowledged, (b) *not disclosed* (absence of evidence, stated as such, not as a fault), and (c) structural limits inherent to the "investigate-the-live-incident" design.
3. Maps each gap to a concrete differentiator of **our** framework, grounded in actual repo code (`rex/scoring.py`, `rex/escalate.py`, `sim/engine.py`, `ARCHITECTURE.md`), not aspiration.

## Approach
- Research via WebSearch + WebFetch on the 4 Datadog primary URLs + 1 independent (Help Net Security).
- Record every claim with an exact-quote where possible and a URL.
- Cross-reference our framework's distinguishing mechanisms (mechanism-level reward, trap penalty, escalation-when-no-safe-fix, frozen-policy eval) to frame the comparison.

## Files to create
- `01..10` step files + `SUMMARY.md` + `result.json` (required by brief).
- `artifacts/bits_ai_sre_analysis.md` — the deliverable analysis (the real artifact).
- `artifacts/claims_table.csv` — machine-checkable table: claim | type | source_url | our_position.
- `artifacts/sources.json` — sourced citation list (validated JSON).
- `artifacts/validate.py` — parse-check the CSV + JSON, assert every claim has a source URL.

## Dependencies / data
- Web access only. No cluster, no Datadog account (we cannot empirically test Bits — noted as a blocker for any *measured* comparison; the analysis is a **claims analysis**, which is exactly the task).

## Risks
- **Straw-manning**: must quote Datadog accurately and label "not disclosed" vs "cannot do."
- **Over-claiming for us**: our differentiators must cite real repo code, and we must concede where Bits is genuinely ahead (production scale, real telemetry breadth).
- **Source drift**: Bits is recently GA (Dec 2025); numbers change between blog versions — cite the specific post.

## Success criteria
- Every Datadog capability claim has a primary-source URL.
- Gaps are categorized (acknowledged / not-disclosed / structural) and fairly labeled.
- Each differentiator cites a real file in this repo.
- `validate.py` passes: CSV + JSON parse, every row has a source.
- At least one honest concession where Bits beats us.
