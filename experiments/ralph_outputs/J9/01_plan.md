# J9 — Plan: Feedback from a real on-call SRE team

## Objective
Get *practitioner* validation (not academic) of the SRE-Degrees thesis: that our
cascading-incident scenarios, the "loudest alert points at the victim, not the cause"
trap, and the root-cause-aware reward actually reflect how real on-call work feels.
The deliverable is a **structured feedback-collection instrument + recruitment plan +
analysis template** that a human operator can execute to run real interviews/surveys.

This is a **coordination task**: the bottleneck is human access (real on-call SREs under
NDA, with limited time), which an autonomous agent cannot itself satisfy. So the win
condition is a *runnable research protocol*, not collected data.

## Approach
1. Define what we actually need to learn (research questions tied to the thesis claims).
2. Build a **survey** (quantitative, 10–12 min, screener + Likert + scenario-realism rating).
3. Build an **interview guide** (45-min semi-structured, tailored to on-call SREs:
   pager fatigue, blast radius, "fix that makes it worse" war stories).
4. Build a **recruitment plan** (where real on-call SREs are, incentives, screener,
   consent, scheduling, target N, sampling frame, anti-bias).
5. Build an **analysis template** (coding scheme, quant aggregation, thesis-claim → evidence
   mapping, how a single interview updates the environment backlog).
6. Document the **human-access blocker** honestly and give the no-human fallback
   (academics / Discord lurk / public post-mortem proxy) with its validity caveats.

## Files to create (all task-namespaced, no shared-core edits)
- `artifacts/sre_feedback_survey.md` — survey instrument (paper form).
- `artifacts/sre_survey.json` — machine-readable survey schema (questions, types, scales).
- `artifacts/sre_interview_guide.md` — 45-min semi-structured guide.
- `artifacts/recruitment_plan.md` — channels, screener, consent, incentives, N, timeline.
- `artifacts/analysis_template.md` — coding scheme + thesis-claim evidence map (human-readable).
- `artifacts/analysis_template.csv` — empty response-coding sheet (real columns, 0 rows).
- `artifacts/thesis_claims.json` — the claims under test, with measurable accept/reject criteria.
- `artifacts/validate_instruments.py` — validator: parses the JSON/CSV, checks every survey
  question maps to ≥1 thesis claim, checks scales are well-formed. Real, runnable.

## Dependencies
- Thesis claims come from `ARCHITECTURE.md` (read). No live API, no cluster, no GPU.
- Python 3.13 stdlib only (json, csv, pathlib) for the validator — no external deps.

## Risks
- **Human access** (primary, unavoidable here): real on-call SREs are scarce, gated by
  employer NDA, and skeptical of surveys. Mitigation = make the instrument *short, credible,
  practitioner-voiced*, and document the blocker honestly; provide proxy fallbacks.
- **Leading questions / confirmation bias**: a survey written by the thesis authors will
  fish for agreement. Mitigation = include reverse-coded items + an open "what's wrong with
  this scenario" prompt + a falsification criterion per claim.
- **Validity theater**: producing a pretty instrument that's never run. Mitigation = be
  explicit in `08`/`09` that no data was collected; status reflects *instrument delivered*.

## Success criteria
1. Survey + interview guide exist, are on-call-SRE-specific (not generic UX surveys), and
   every quantitative item maps to a falsifiable thesis claim.
2. Recruitment plan is concrete: named channels, a screener that excludes non-on-call
   respondents, incentive, consent, target N with justification, timeline.
3. Analysis template turns raw responses into a claim-by-claim accept/reject verdict.
4. `validate_instruments.py` runs green: JSON parses, CSV header matches schema, 100% of
   survey items map to a thesis claim, no orphan claims.
5. The human-access blocker is documented honestly; no fabricated responses anywhere.
