# J9 — SUMMARY

**Task:** Get feedback from a real on-call SRE team (not academics). Coordination task.
Deliver a feedback-collection instrument (survey + interview guide), a recruitment plan, and an
analysis template; document the human-access blocker honestly. No shared-core edits.

## Delivered (all in experiments/ralph_outputs/J9/artifacts/)
- **thesis_claims.json** — 5 falsifiable claims (cascade realism, naive-fix trap, reward-tier
  ordering, scenario specificity, agent trust) with pre-registered flag-based accept/reject criteria + COI disclosure.
- **sre_survey.json** + **sre_feedback_survey.md** — 12-min practitioner survey, war-story-first,
  *elicit-then-reveal* (our reward framing shown last), reverse-coded trust item, on-call screener.
- **sre_interview_guide.md** — 45-min semi-structured guide with verbatim scripts, INT_* tags, elicit-before-reveal reward block.
- **recruitment_plan.md** — 6 named channels (Rootly/incident.io/FireHydrant, SREcon, r/sre,
  on-call Discords, warm net; LinkedIn last), screener, no-proprietary consent, incentive,
  target N (survey 25-40 / interviews 8-12) with justification, 4-week timeline, anti-bias cap.
- **analysis_template.md** + **analysis_template.csv** — coding scheme, Cohen's kappa, flag-based
  claim verdicts, >=2-flag per-scenario review trigger, counts+quotes (no population means). CSV = header + 0 rows.
- **validate_instruments.py** — stdlib validator (5 checks); runs **green** (exit 0); caught and forced a real fix.

## Verification
validate_instruments.py: exit 0 — 15 survey questions (12 claim-bearing), 5 claims all covered,
no orphan claims, all scales valid, CSV records every item. Caught 2 real bugs during testing
(un-recordable free-text follow-ups), fixed. JSON/CSV/Markdown all parse.

## Blocker (honest)
**No real on-call SRE was contacted; no response data exists.** Human access (recruitment,
consent, scheduling, ethics) is outside an autonomous agent's reach. The literal goal "get
feedback" is NOT achieved; the specified deliverable (runnable instrument + recruitment plan +
analysis template) IS, and is machine-validated. Lower-validity fallback documented: public
post-mortems as a proxy for C1/C2 only (cannot test C3 reward ordering or C5 trust).

**Status: completed** (real instrument + spec + tests delivered; downstream data-collection blocked on human access, documented).
