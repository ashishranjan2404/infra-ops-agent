# J9 — Implementation

## What I built (all under experiments/ralph_outputs/J9/artifacts/, no shared-core edits)

1. **thesis_claims.json** — 5 falsifiable claims (C1 cascade realism, C2 naive-fix trap,
   C3 resolution ordering vs our reward tiers, C4 scenario specificity, C5 agent trust). Each
   has a pre-registered flag-based accept/reject/review criterion and a COI disclosure.

2. **sre_survey.json** — machine-readable survey schema: 3 scales, 5 pages, 15 questions
   (12 claim-bearing). Order enforces *elicit-then-compare*: screener -> war-story open
   elicitation -> pattern frequency -> scenario realism -> (our framing revealed last) ->
   reward compare + trust. Includes a reverse-coded trust item and a screen-out on S1.

3. **sre_feedback_survey.md** — human-readable render of the survey, practitioner-voiced,
   12-min cap, COI line at top.

4. **sre_interview_guide.md** — 45-min semi-structured guide with verbatim opening/closing
   scripts, time budget, INT_* section tags matching `tested_by`, elicit-before-reveal on reward.

5. **recruitment_plan.md** — named channels (Rootly/incident.io/FireHydrant communities,
   SREcon, r/sre, on-call Discords, warm network; LinkedIn last resort), screener, explicit
   no-proprietary consent, incentive (gift card or charity donation), target N (survey 25-40,
   interviews 8-12) with justification, 4-week timeline, anti-bias channel-cap rule.

6. **analysis_template.md** + **analysis_template.csv** — coding scheme (7 codes), Cohen's
   kappa inter-rater reliability, claim-verdict table, per-scenario >=2-flag review trigger,
   counts+quotes (no population means). CSV = header + 0 data rows (empty by design). Folds in
   the ouroboros coder rules (C3 urgency rule, C4 interview-weighting, C1 quality gate).

7. **validate_instruments.py** — stdlib validator. 5 checks: JSON parses; every claim-bearing
   question maps to a real claim; no orphan claims; scales resolve; CSV records every
   claim-bearing item. Runs **green** (exit 0).

## Shared-core changes proposed: NONE
This is a coordination/research task. It produces no code changes to rex/sim/agent. The only
forward link to the codebase is conceptual: C4 review flags would feed back into
`scenarios/cidg/generated/*.yaml` authorship — but that is a *human* follow-up after data is
collected, not an edit made here.

## How a result flows back into the project
Survey/interview -> analysis_template -> claim verdicts + scenario backlog -> (human) revises
specific CIDG scenarios and possibly the reward-tier copy. The instrument is the missing
top-of-funnel; everything downstream already exists in the repo.
