# 02_grill — 5 personas, 3 rounds

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR:** Outreach is a means, not the end. The thing I actually want is *distribution shift*
data: our `scenarios/cidg` set is reverse-engineered from public blog posts, so it inherits
the survivorship bias of "incidents interesting enough to blog about." Real anonymized alert
streams + timelines would let us measure whether our auto-harness generalizes. The brief must
make the *research value-add to them* concrete, or it's spam.

**PSRE:** As the person on the other side of this email, my first reaction to "can we have your
incident data" is "absolutely not, that's our crown jewels and a legal liability." You will get
ignored unless you (a) prove you already respect our public material, (b) ask for the *least
sensitive useful slice*, and (c) make the anonymization our lawyers' problem trivial.

**REV:** For a paper, the provenance and ethics of the data matter as much as the numbers. If
A5 yields a real partnership, you need a data-use agreement and an anonymization protocol you
can *cite*. Vague "we'll anonymize it" gets desk-rejected on ethics. I want a written spec.

**RLE:** I care about format. If they send me a 40-page PDF postmortem I can't turn it into a
`cidg` scenario without a week of hand-parsing. The ask should specify a *machine-friendly*
shape (JSON timeline, alert payloads) or we've created work we can't absorb.

**DOL:** Realistically these companies move slowly. The win condition for A5 is not "data in
hand" — it's "a warm thread open with the right person." The tracking sheet and the contact
path matter more than the prose of the email.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**PSRE → SMR:** I disagree with SMR's framing that raw alert streams are the prize. No SRE org
will ever hand a research group their raw alert stream — it leaks topology, headcount,
customers, and on-call patterns. If you ask for that you get a zero reply rate. Ask instead for
*structured, already-curated* postmortem internals (timeline + decision points) of incidents
they've *already chosen to disclose publicly*. Lower value per record, but >0 reply rate beats
infinite value at 0% yield.

**RLE → REV:** REV wants a citable formal protocol, but I think over-engineering the
anonymization spec up front kills the deal. A partner engineer reading a dense k-anonymity
formal contract before any relationship exists will bounce. I'd lead with a *one-paragraph*
plain-English promise and keep the formal JSON schema as an appendix they only see if they're
already interested.

**REV → RLE:** Pushing back on RLE — "appendix only" is how you end up with an ethics section
you can't defend in review. The formal spec doesn't need to be *sent first*, but it must
*exist* and be referenced. I accept it lives in an attachment, not the email body. So we're
actually disagreeing about placement, not existence.

**DOL → SMR:** SMR keeps optimizing for the ideal dataset. I'll be blunt: the most likely
outcome of A5 is *no data at all* from all three. incident.io is the only plausible yes because
it serves their business. If we write three briefs that assume eventual success we're lying to
ourselves. The brief for Cloudflare and CircleCI should explicitly carry a "likely-no, here's
the fallback (keep using public postmortems)" line.

**SMR → DOL:** Conceding to DOL — yes, expected yield is low, and I was over-indexing on the
ideal dataset. But I reject the implication that low-yield outreach is worthless: even a *"no,
but you can keep using our public postmortems / here's our RSS of postmortems"* answer is a
real, citable permission signal that strengthens the paper's data-provenance story.

## Round 3 — synthesis

Consensus:
1. **Ask for the least-sensitive useful slice**, not raw streams (PSRE wins over SMR's ideal).
   Concretely: structured internals (timeline JSON, alert payload shapes, remediation steps) of
   incidents they have *already publicly disclosed* — we're asking them to "un-strip" the blog.
2. **Warm hook first**: open by showing we already model their public incidents in `cidg`.
   This is our unfair advantage and every email leads with it.
3. **Anonymization spec exists and is citable (REV) but is an attachment, not the email body
   (RLE).** One-paragraph promise in the email; formal JSON schema + redaction rules attached.
4. **Be honest about yield (DOL).** Each brief states the realistic outcome and the fallback
   (continue using public postmortems, which we are already permitted to do). incident.io is
   ranked highest-probability; Cloudflare medium (research-friendly culture); CircleCI lower.
5. **Format-first ask (RLE).** Email specifies the machine-friendly shape we can ingest.
6. **Tracking sheet is the real success metric (DOL), not data-in-hand.**
