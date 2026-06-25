# A4 — Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DEVOPS** (DevOps Lead).

## Round 1 — initial takes

**SMR:** An outreach task can't move the research forward by itself, but the
*framing* can. Don't ask Snorkel for "incident logs" — that reads like free-data
panhandling. They sell expert data. Ask for a research collaboration on an *open*
SRE/incident RL benchmark; that aligns with their $3M Open Benchmarks Grants. The
artifact that matters is the schema — if we can show data drops cleanly into a
runnable verifier, we look credible, not needy.

**PSRE:** Raw incident logs are radioactive. Real prod logs carry hostnames,
internal IPs, customer identifiers, employee names in postmortems, security
details. No company ships those without an NDA and heavy redaction. The realistic
ask is *anonymized, structured* incident records — symptom, trap action, root
cause, fix — exactly the shape of our existing catalog. Don't ask for tarballs of
Splunk output; ask for the postmortem-grade structured form.

**REV:** As a reviewer I don't care about the email. I care whether the resulting
data is admissible. If Snorkel data is itself *synthesized by experts* (which is
their whole model), then it is NOT "fully real incidents" and doesn't close the
gap `INCIDENT_DATASET.md` flags ("0 fully real incidents"). Be honest in the brief
about what class of evidence this yields, or you'll mislead the paper.

**RLE:** The thing I want from a partner is *runnable environments with verifiable
rewards*, not a static dataset I have to re-encode by hand. Snorkel literally
builds RL gyms with deterministic verifiers — that's the high-value ask. The
schema should capture the *verifier contract* (trap actions, canonical fix steps,
SLO assertions), not just prose.

**DEVOPS:** Whoever sends this needs a contact that exists and a CTA that a busy
person can say yes to in 30 seconds. "Talk to a data researcher" / partner form is
real; a guessed personal email is not and will bounce or annoy. Keep the email
short, one ask, one link to the schema.

## Round 2 — react to another persona (genuine disagreement)

**RLE → REV:** I disagree with REV's purism. "Fully real raw logs" is a fetish.
For RL what matters is whether the *causal structure* (symptom ≠ root cause, a
trap action exists) is faithful and verifiable. An expert-reconstructed incident
with a correct verifier is *more* useful to training than a raw log dump we can't
grade. The gap to close isn't "rawness," it's "novel + verifiable + not authored
by us." Snorkel data is authored by *them*, which already breaks our self-authored
contamination problem.

**REV → RLE:** That's exactly the sleight of hand I'm flagging. If both our
scenarios and Snorkel's are expert-authored, you haven't escaped the "synthetic"
critique — you've just changed who held the pen. A skeptical reviewer will say
"all your incidents are constructed." The brief must not claim this closes the
real-incident gap. It mitigates the *self-authoring/contamination* gap, which is a
different, narrower win. Conflating the two is how papers get desk-rejected.

**PSRE → SMR:** SMR wants to lead with "open benchmark collaboration." I push
back: Snorkel's open-grants track may have its own scope and timeline, and we
don't control whether we'd get usable incident-specific data out of it. Lead with
the *concrete mutual artifact* (an open SRE incident eval), but keep a fallback
ask — "even a handful of anonymized structured records under NDA would let us
validate the schema." One big ask + one small fallback converts better than a
single moonshot.

**DEVOPS → PSRE:** Agreed on radioactivity, but you're over-rotating on NDA-first.
If the *first* email leads with NDA/legal, it dies in triage. Put legal in a
separate checklist (internal), and let the email propose a low-friction first
step: a 30-min call. Legal gating happens *after* mutual interest, not in cold
outreach.

**SMR → DEVOPS:** Fine on tone, but don't make it so light it's content-free. The
differentiator is that we arrive with a *schema and a verifier-shaped ask*. Busy
researchers respond to "we did our homework, here's the exact data contract"
more than to "let's chat." Attach substance.

## Round 3 — synthesis

Consensus the artifacts must reflect:
1. **Position as collaboration, not a handout** — open SRE/incident RL benchmark,
   tied to Snorkel's RL-environments + Open Benchmarks Grants framing (SMR, RLE).
2. **Ask for anonymized, structured, verifier-ready records or a runnable env** —
   never raw prod logs (PSRE, RLE).
3. **Tiered ask:** big (co-built open benchmark) + small fallback (a few NDA'd
   structured records to validate the schema) (PSRE, SMR).
4. **Be honest about evidence class:** this addresses *self-authoring /
   contamination*, NOT the "0 fully real raw incidents" gap. Say so in the brief
   (REV).
5. **Only real contact paths; sending is out of scope; flag unverifiable bits**
   (DEVOPS).
6. **Schema captures the verifier contract** (trap actions, canonical fix steps,
   SLO assertions), and maps onto existing scenario YAML (RLE).
7. **Legal/data-sharing as a separate gating checklist, not in the cold email**
   (DEVOPS vs PSRE resolved).
