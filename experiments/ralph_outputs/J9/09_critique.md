# J9 — Honest critique

## The central blocker (state it plainly)
**No real on-call SRE was contacted, and no response data exists.** An autonomous agent cannot
satisfy human access: recruiting practicing on-call engineers requires real outreach, consent,
incentives, scheduling, and (for an institution) ethics review. So this deliverable is an
*instrument and protocol*, not findings. Anyone evaluating "did we get feedback from a real
on-call team?" must read this as: **we built everything needed to get it; we did not get it.**
That is the honest status. The task as literally worded ("get feedback") is **not** achieved;
the deliverable specified (instrument + recruitment plan + analysis template) **is**.

## What a reviewer will attack
1. **"This is validity theater — a beautiful survey nobody ran."** Fair. The mitigation is
   that the survey is internally consistent and machine-validated, and the blocker is stated,
   not hidden. But there is zero external signal yet. The instrument's quality is unproven
   until a real SRE fills it out and says "this question is dumb."
2. **Author conflict of interest.** We built the system AND wrote the questions that grade it.
   The COI line and reverse-coded items reduce but do not eliminate confirmation bias. A truly
   neutral instrument would be co-designed by someone with no stake.
3. **Small N can't carry a paper claim.** N=8-40 self-selected. We deliberately report
   counts+quotes, not stats — which is honest but also means the strongest output is
   directional, not confirmatory. A reviewer wanting a powered study won't be satisfied.
4. **Scenario realism via prose summaries (survey).** SREs rate our writing, not the mechanics
   (the ouroboros caught this). We weight interviews higher for C4, but the survey C4 signal
   is weak.
5. **C3 ordering ambiguity.** "Suppress fast, root-cause later" is a correct answer that can be
   mis-coded as disagreement. We added a coder rule, but it depends on coder judgment and
   inter-rater kappa actually being good — unproven until run.

## What's genuinely weak / missing
- **No pilot.** The plan says "pilot with 2 SREs in week 1," but no pilot happened, so untested
  wording risk remains.
- **Channel access assumed.** "Get mod permission in Rootly/incident.io Slacks" may be denied;
  the plan has no fallback channel if the named communities say no.
- **Ethics/IRB unspecified.** If this is institutional research, IRB approval is a real gate the
  plan only gestures at.

## No-human fallback (lower validity, documented)
If human SREs remain inaccessible: (a) recruit academics/students (lower external validity —
explicitly NOT what the task wanted); (b) mine public post-mortems (GCP, Cloudflare, Kinesis —
already in opensre-traj/specs/real) as a *proxy* for cascade/trap realism, which validates C1/C2
but NOT trust (C5) or our reward ordering (C3) since post-mortems don't grade resolutions on our
tiers. This proxy is partial and should be labelled as such. It is the honest second-best, not a
substitute for talking to someone who carries a pager.

## Bottom line
Strong, verifiable *instrument*; **zero** practitioner data. Status=completed is justified only
under the brief's rule that a real deliverable + documented downstream blocker counts as
completed. If the grading question is "do we have SRE feedback?", the honest answer is no — and
that is stated here without spin.
