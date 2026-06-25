# Recruitment plan — real on-call SREs (not academics)

## Goal & target N
- **Survey:** N = 25–40 completed (after screen-out). At this N we report **counts + quotes**,
  not population means (see analysis template). Justification: scenario-realism flags and
  pattern-recognition counts saturate quickly; we need breadth of incident types, not a
  statistically powered estimate.
- **Interviews:** N = 8–12 semi-structured. Justification: qualitative saturation for
  cascade/trap/reward themes typically plateaus around 8–12 for a focused population; beyond
  that, marginal new themes drop sharply.
- **Sampling frame:** practitioners *currently or recently (≤12 mo) on a production pager
  rotation*. The screener hard-excludes non-on-call respondents and pure managers/academics.

## Channels (where real on-call SREs actually are)
| Channel | Type | Approach | Why it reaches on-call engineers |
|---|---|---|---|
| Rootly / incident.io / FireHydrant communities (Slack) | Survey + interview | Post in #general/#random with mod permission; DM volunteers | These tools are *for* on-call teams |
| SREcon / Monitorama attendees & mailing lists | Interview | Recruit at hallway track; follow up by email | Self-selected practicing SREs |
| r/sre, r/devops, r/kubernetes | Survey | Single non-spammy post, flair-compliant | Large practitioner readership |
| On-call-focused Discords (e.g. CNCF, observability communities) | Both | Ask mods; pinned message | Active operators, not vendors |
| Personal/2nd-degree network of practicing SREs | Interview | Warm intros (highest yield, lowest bias risk per channel) | Highest completion + trust |
| LinkedIn — **last resort** | Interview | Targeted, *not* cold-blast | Low signal, high bias; only for hard-to-reach seniority |

Anti-bias note: no single channel should exceed ~40% of the sample; over-weighting our own
network inflates agreement. Log channel per respondent (column in CSV) and report the mix.

## Screener (gate at survey start = `S1_oncall`)
- Must answer **"primary," "secondary," or "within 12 months"** to S1. Anyone answering "No"
  is thanked and exited (response discarded from analysis, counted in funnel).

## Incentive
- **Survey:** entry into a draw for a small gift card, OR a donation to a charity of choice
  per completion (donation framing yields less biased responses than direct payment).
- **Interview:** $50–75 gift card OR equivalent charitable donation for 45 min. Offer the
  aggregated anonymized findings back — practitioners value the benchmark.

## Consent (must be explicit, captured before any data)
1. Purpose stated + **conflict-of-interest disclosure** (we built the system).
2. **No proprietary / employer-confidential information** clause — respondent agrees to keep
   examples generic; we agree to redact anything identifying on intake.
3. Voluntary, withdraw anytime; interviews recorded only with explicit yes; recordings deleted
   after coding.
4. Anonymized aggregate use only; no employer names published.

## Timeline (operator-executable)
| Week | Action |
|---|---|
| 1 | Get mod permissions; finalize consent + IRB/ethics check if institutional; pilot survey with 2 friendly SREs, fix wording |
| 2 | Launch survey across channels; open interview signup |
| 3 | Run interviews (target 2–3/day max to keep coding quality); chase survey N |
| 4 | Close collection; 2-coder analysis (κ); produce claim-by-claim verdict; backlog scenario-review items |

## Risks specific to recruitment
- **NDA chilling effect:** mitigated by explicit "generic examples only" framing up front.
- **Self-selection toward enthusiasts:** mitigated by the reverse-coded trust item + open
  "call BS" prompt that rewards criticism; report channel mix.
- **Low completion on long survey:** mitigated by 12-min cap and war-story-first ordering.
