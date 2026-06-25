# On-call incident response — practitioner reality check (survey)

**~12 minutes. No proprietary or employer-confidential details — keep examples generic.**

> **Conflict of interest:** we built the autonomous-incident-response training system you're
> evaluating. Please be brutal; agreement is not the goal, accuracy is.

Human-readable rendering of `sre_survey.json`. Order is intentional: we ask you to describe
your own experience **before** we reveal how *we* think about it, so we don't lead you.

---

## Section 0 — Screener (excludes non-on-call respondents)

- **S1.** Are you currently in an on-call / pager rotation for production systems?
  ◻ Yes, primary ◻ Yes, secondary/backup ◻ Not now but within 12 months ◻ No → *(no = thank you, end)*
- **S2.** Years of hands-on production on-call experience? ◻ <1 ◻ 1–3 ◻ 3–7 ◻ 7+
- **S3.** Roughly how many services are you paged for? ◻ 1–5 ◻ 6–20 ◻ 21–100 ◻ 100+ / microservices

## Section 1 — Your war stories (free text, FIRST — before our framing)

- **Q_warstory** *(required):* Tell us about an incident where the **loudest alert pointed at
  the wrong service** — the page fired on something that was actually a downstream victim of
  the real cause. What happened?
- **Q_elicit_good_bad** *(required):* In your own words, **before we tell you ours**: what
  separates a GOOD incident resolution from a BAD one that merely "looks resolved"? Rank the
  kinds of outcomes from best to worst.
- **Q_trap_example:** Describe a time the **obvious fix made things worse** (a restart /
  rollback / scale-up that deepened the outage).

## Section 2 — How common are these patterns? (Never · Rarely · A few times · Often · Constantly)

- **Q_loudest_alert_freq:** How often does the loudest alert point at a *victim* rather than the root cause?
- **Q_trap_seen:** How often does the naive/obvious remediation make an incident *worse*?

## Section 3 — Scenario realism (3 anonymized scenarios shown, rotated from our 33)

Rate each: **Toy/contrived · Somewhat off · Plausible · This literally happened to me**

- **Q_scenario_realism:** scenario_A ◻◻◻◻  scenario_B ◻◻◻◻  scenario_C ◻◻◻◻
- **Q_scenario_bs:** Which (if any) would you **call BS on**, and why? What's missing or wrong?

## Section 4 — Our grading & trust (our framing revealed HERE for the first time)

Likert: **Strongly disagree → Strongly agree**

- **Q_tier_compare:** We grade — *clean root-cause fix = best; symptom suppressed but cause
  still live = partial; obvious-fix-made-it-worse = penalised*. Does this ordering match how
  you'd grade it?
- **Q_tier_worse_case:** Is there an outcome **worse** than "made it worse," or a case our
  ordering gets wrong?
- **Q_trust_agent:** An agent that reliably names root cause + a safe fix + avoids the trap
  would be a useful on-call triage co-pilot for me.
- **Q_trust_reverse** *(reverse-coded):* I would **not** act on such an agent's diagnosis
  without fully re-verifying it myself.
- **Q_trust_conditions:** What would the agent have to prove before you'd trust it during a real page?

---

*Thank you. If you opted in, we'll send the aggregated (anonymized) findings.*
