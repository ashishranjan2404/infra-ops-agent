# Semi-structured interview guide — on-call SREs (45 min hard cap)

**Format:** 1:1, video or call, recorded with consent. Semi-structured: the questions below
are a spine, not a script — chase the war stories. One interviewer + one note-taker (note-taker
double-codes for inter-rater reliability, see analysis template).

**Opening script (read verbatim):**
> "Thanks for the time. I build training scenarios for autonomous incident-response agents,
> and I want a real on-call engineer to tell me where they're realistic and where they're
> nonsense. Full disclosure: I built the thing I'm asking you to critique, so please don't be
> polite. Nothing you say needs to include proprietary or employer-confidential details —
> keep it generic. I'll record if that's OK; I can stop anytime. Sound good?"

**Time budget:** Warmup 5 · Cascade/war-story 10 · Trap 8 · Reward elicitation 10 ·
Scenario walkthrough 8 · Trust 4.

---

## 0. Warmup (5 min)
- What system are you on-call for, roughly? Pager volume on a bad week?
- Walk me through the last page that actually scared you (generic).

## 1. Cascade realism — claim C1 (10 min) [INT_cascade]
- Have you had an incident where the **loudest alert was on the wrong service** — a downstream
  victim, not the cause? Tell me the whole arc.
- How did you figure out it wasn't the alerting service? What misled you first?
- How common is "alert points at the victim" in your experience — one-off or a pattern?
- *Probe:* what tooling/signal eventually pointed you at the real root cause?

## 2. The trap — claim C2 (8 min) [INT_trap]
- Tell me about a fix that **made it worse** — the restart/rollback/scale that backfired.
- At the moment you did it, why was it the obvious move? What would've warned you off?
- How often does the "obvious" remediation deepen an outage vs help?

## 3. Reward elicitation — claim C3 (10 min) [INT_reward] — ELICIT BEFORE REVEAL
- *(Elicit first, do NOT show our tiers yet.)* Rank these for me: (a) root cause fixed and
  gone, (b) symptoms gone but root cause still lurking, (c) you did something that made it
  worse. Best to worst — and *why* in that order?
- Is there an outcome **worse** than (c)?
- *(Now reveal our tiers: 1.0 / 0.45 / −0.60.)* Here's how we grade. Where do we get it wrong?
- *Probe:* does "back up fast but cause live" ever deserve MORE credit than we give it? When?

## 4. Scenario walkthrough — claim C4 (8 min) [INT_scenario_walkthrough]
- *(Show 1–2 anonymized CIDG scenarios, e.g. redis-cache-flush, auth-cert-expiry.)*
  Read this like it's your page. What do you do first? Does it ring true?
- What's missing that a real version of this would have? What would you call BS on?
- Which of our scenarios would you *never* see in production, and why?

## 5. Trust — claim C5 (4 min) [INT_trust]
- If an agent reliably named the root cause + a safe fix + flagged the trap, would you use it
  on a real page? As what — co-pilot, auto-remediator, post-hoc reviewer?
- What would it have to **prove** before you'd act on it at 3am?

## Close (verbatim)
> "Anything I should've asked and didn't? Anyone else on a pager I should talk to?"

**Post-interview (interviewer, within 1h):** fill the response row in `analysis_template.csv`,
log 2–3 verbatim quotes per claim, note any scenario flagged unrealistic (triggers C4 review).
