# Analysis template — turning responses into a claim-by-claim verdict

> **Small-N discipline (pre-registered):** N is 8-40. We report **counts and verbatim quotes**,
> NOT Likert population means. Likert items are used only as *within-respondent* signal and are
> labelled non-inferential. We do not compute p-values. We disclose the author conflict of
> interest in the write-up.

## 1. Data intake
- One row per respondent in `analysis_template.csv` (schema = survey + interview ids + meta).
- Redact any proprietary detail on intake (consent requires generic examples).
- Record `channel` and `source` (survey/interview) per row for the anti-bias mix report.
- **Quality gate:** drop incomplete/drive-by war-stories from the C1 tally (a one-line
  non-answer is not evidence). Note exclusions in the funnel.

## 2. Coding scheme (qualitative free-text -> flags)
Each free-text answer is coded by **two coders independently**, then reconciled. Codes:

**Coder rules (from ouroboros review):**
- **C3 urgency rule:** "suppress symptoms fast on a customer-facing P1, root-cause later" is a
  legitimate *time-horizon* answer, NOT `ordering_conflicts`. Only tag `ordering_conflicts`
  when a respondent genuinely de-prioritizes root cause as an end state (would leave the cause
  live and call it done). This prevents a false REJECT of C3.
- **C4 weighting:** survey scenario-realism rates our *prose summary*; interview walkthroughs
  rate the *mechanics*. Weight interview evidence above survey for C4 verdicts.


| Code | Applies to | Meaning |
|---|---|---|
| `cascade_confirmed` | Q_warstory, INT_cascade | Describes a real loud-alert-on-victim incident |
| `trap_confirmed` | Q_trap_example, INT_trap | Concrete naive-fix-made-worse example |
| `ordering_matches` | Q_elicit_good_bad, INT_reward | Open-elicited ordering matches our tiers (before reveal) |
| `ordering_conflicts` | same | Orders outcomes in a way that contradicts our reward signs |
| `scenario_unrealistic:<id>` | Q_scenario_bs, INT_scenario | Flags a specific scenario as BS/contrived |
| `trust_conditional` | Q_trust_*, INT_trust | Would use as co-pilot under stated conditions |
| `trust_refused` | same | Would not trust under any near-term condition |

**Inter-rater reliability:** compute Cohen's kappa over the two coders on the binary presence of
each code across all rows. Report kappa; if kappa < 0.6 on any code, re-reconcile that code's
definition and re-code. (kappa is descriptive here, not a significance test.)

## 3. Claim verdicts (apply pre-registered criteria from `thesis_claims.json`)
For each claim, tally the relevant codes across **independent** respondents and apply its
`accept_if` / `reject_if` / `review_if`:

| Claim | Evidence tally | Verdict (ACCEPT / REJECT / REVIEW) | Key quotes (>=2) |
|---|---|---|---|
| C1_cascade_realism | # cascade_confirmed = ___ | ___ | "___" / "___" |
| C2_naive_fix_trap | # trap_confirmed = ___ | ___ | "___" / "___" |
| C3_resolution_ordering | matches=___ conflicts=___ | ___ | "___" / "___" |
| C4_scenario_specificity | per-scenario flag counts: see s4 | ___ | "___" / "___" |
| C5_agent_value | conditional=___ refused=___ | ___ | "___" / "___" |

## 4. Per-scenario review trigger (C4)
For every CIDG scenario shown, count independent `scenario_unrealistic:<id>` flags.
**>=2 flags => mandatory documented review** of that scenario. Output a table:

| scenario_id | # unrealistic flags | review triggered? | reviewer note / action |
|---|---|---|---|
| 40-redis-cache-flush | ___ | yes/no | ___ |
| 42-auth-cert-expiry | ___ | yes/no | ___ |
| ... | | | |

## 5. Outputs of the analysis
1. **Claim verdict table** (s3) - ACCEPT/REJECT/REVIEW per thesis claim, with quotes + kappa.
2. **Scenario backlog** (s4) - concrete review/fix items for flagged scenarios.
3. **Channel-mix report** - % of respondents per channel (bias check; no channel > ~40%).
4. **Trust-conditions list** (C5) - what SREs said the agent must prove; feeds product/eval backlog.
5. **Honest limitations paragraph** - N, self-selection, COI, no inferential stats.
