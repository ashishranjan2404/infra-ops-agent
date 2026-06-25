# J9 — Improved Plan (post-grill)

## What changed vs `01_plan.md`

### Accepted critiques
1. **Practitioner voice / length caps (PS).** Survey re-ordered to open with a mandatory
   *war-story* free-text prompt ("an incident where the loudest alert was on the wrong
   service"). Hard caps: survey ≤ 12 min, interview ≤ 45 min. Removed any abstract
   "rate our reward decomposition" as an opener.
2. **Elicit-then-compare (PS + RE).** Added a mandatory open-elicitation block: respondent
   describes what separates a *good* from a *bad* incident resolution **before** we reveal
   our reward tiers. Only afterward do we show the tiers and ask "is there a worse-than-trap
   case we missed?" This gets an unbiased prior plus a comparable item.
3. **Pre-register the process, not brittle thresholds (SR + AR + DL).** `thesis_claims.json`
   now encodes, per claim, a **flag-based qualitative criterion** (e.g. "≥2 independent SREs
   flag scenario as unrealistic ⇒ mandatory documented review") instead of a fragile
   percentage gate. The *process* is pre-committed; outcomes must be documented either way.
4. **No misleading stats at small N (AR).** Analysis template reports **counts + verbatim
   quotes**, not Likert population means. Likert items are kept only as *within-respondent*
   ranking signal and explicitly labelled non-inferential. Inter-rater reliability (Cohen's
   κ on a 2-coder subset) is part of the template.
5. **Recruitment as a first-class deliverable (DL).** `recruitment_plan.md` names concrete
   channels (Rootly/incident.io communities, SREcon, r/sre, on-call Discords/Slacks), an
   explicit **"no proprietary / no employer-confidential info"** consent clause, a real
   incentive, and a screener that excludes anyone not currently on a pager rotation.
6. **Conflict-of-interest disclosure (AR).** A standing COI statement ("the instrument's
   authors built the system under evaluation") is added to consent + analysis write-up, and
   the survey carries a neutral framing line.

### Rejected critiques (and why)
- **RE's original "make them rank our reward tiers first"** — rejected. Ranking pre-baked
  outcomes inside our worldview confirms the prior instead of testing it. Replaced by
  elicit-then-compare (open ordering first, our tiers revealed second). RE conceded this.
- **AR's fixed-percentage accept gate** (e.g. "70% must agree") — rejected for N≈8–12: it
  fails from sampling noise alone and would discard good scenarios. Replaced by DL's
  flag-based review trigger, but pre-committed as a *process* per SR's amendment, so we can't
  rationalize away bad signal.

## Net deliverable set (unchanged file list, upgraded content)
- `sre_feedback_survey.md` + `sre_survey.json` — war-story-first, elicit-then-compare,
  reverse-coded items, COI line.
- `sre_interview_guide.md` — 45-min semi-structured, war-story spine.
- `recruitment_plan.md` — named channels, screener, consent w/ no-proprietary clause, incentive, N, timeline.
- `analysis_template.md` + `analysis_template.csv` — counts+quotes, flag triggers, κ reliability.
- `thesis_claims.json` — claims with flag-based qualitative accept/reject criteria.
- `validate_instruments.py` — checks every survey item maps to ≥1 claim, no orphan claims, scales well-formed.

## Success criteria (sharpened)
- Every quantitative survey item references a `thesis_claims.json` claim id (validator-enforced).
- Survey opens with mandatory open elicitation; our framing appears only after.
- Recruitment plan excludes non-on-call respondents via screener; consent bars proprietary info.
- Analysis template produces a per-claim accept / reject / review verdict from counts + quotes, with κ reported.
- Human-access blocker documented honestly; zero fabricated responses.
