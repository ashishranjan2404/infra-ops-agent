# A3 — Ralph Loop Grill (5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (AAAI)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR:** From a data standpoint, "fully real, first-party donated" incidents are gold
*if* they have the cascade shape we need (loud victim symptom, trap action, correct fix).
But donor data is noisy and unlabeled. The outreach pipeline must include a *labeling/intake
contract*, otherwise we get 10 raw Slack dumps we can't turn into graded scenarios. Make the
intake schema force the contributor to name the trap action and the root cause.

**PSRE:** The hardest part isn't writing emails — it's that companies will not hand over raw
incident channels. Those contain customer names, internal hostnames, security details. Any
realistic pipeline must lead with anonymization and a narrow ask: "the alert text, the
timeline of actions, and what the real root cause was — de-identified." Lead with reciprocity:
offer them the graded scenario back as a training artifact.

**AAAI:** For the paper, the *provenance* claim is what matters. If A3 just relabels public
postmortems we already have 19 of those — reviewers will say "novelty?" The deliverable must
clearly distinguish (a) public-postmortem-derived vs (b) first-party-donated, and track
provenance per incident. Also: a target list and templates are *process*, not results. Be
honest that this is infrastructure, not 10 incidents in hand.

**RLE:** Whatever comes in must map 1:1 onto `specs/real/*.json` or it's useless to the
training loop. The intake schema should be a strict subset/superset of the real-spec format
so a donated incident becomes a runnable scenario with minimal transform. Validate that.

**DOL:** A tracking sheet is fine but who *runs* the campaign? An autonomous agent can't send
mail. Be explicit this is a runbook a human executes. Also include warm paths — the project
already has relationships (incident.io, HUD community, the conferences). Cold outreach to
FAANG SRE orgs has ~0% yield; communities (SREcon, r/sre, incident.io Slack) yield far more.

## Round 2 — react to another persona (genuine disagreement)

**PSRE → SMR:** I disagree with SMR's "force the contributor to label the trap action."
If you make the intake form heavy, donors bounce. The whole point of *first-party* data is
that the contributor witnessed the trap — but they'll write two sentences, not fill a 12-field
form. Make labeling *optional-but-incentivized*: capture the raw timeline first, let *us* do
the cascade labeling. A heavy form kills response rate; that's the actual bottleneck, not
label quality.

**SMR → PSRE:** Pushing back — if we label it ourselves from a two-sentence donation, we've
reinvented the public-postmortem pipeline we already have, just with a private source. The
*value* of first-party data is the donor's ground-truth on what the trap was and why naive
fixes failed. I'll concede the form can be short, but the trap-action and root-cause fields
must be **required free-text**, not structured. One sentence each is fine.

**AAAI → DOL:** I disagree that warm communities are sufficient. SREcon/Reddit donations are
self-selected and often *already public* (people share what they already blogged). That
*reintroduces* the provenance problem I raised. To make the "fully real / non-public" claim
defensible we specifically need 2-3 companies under a light data-use agreement giving
genuinely unpublished incidents — even if it's a smaller, harder list. Breadth from communities
is fine for volume but won't carry the novelty claim alone.

**DOL → AAAI:** Fair, but a light DUA with a company is a multi-week legal process an agent
can't do, and even a human needs a sponsor inside. I'll concede we should *flag* a small "DUA
track" in the target list, but the realistic near-term yield is community + warm contacts.
Don't let the perfect (signed DUAs) block shipping the machinery.

**RLE → AAAI:** Provenance tagging is cheap — I'll just add a `provenance` enum field
(`public_postmortem` | `first_party_donated` | `first_party_nonpublic`) to the schema. That
resolves AAAI's concern without blocking the pipeline: we accept everything, tag it, and can
filter to the non-public subset for the novelty claim later.

## Round 3 — synthesis

Consensus:
1. **Intake schema maps 1:1 to `specs/real/*.json`** (RLE) and carries a `provenance` enum
   (RLE/AAAI) so we can filter the genuinely-novel subset.
2. **Short form, but `root_cause` and `trap_action` are required free-text** (SMR/PSRE
   compromise) — captures the first-party ground truth without killing response rate.
3. **Anonymization-first, reciprocity-first** outreach (PSRE): narrow de-identified ask,
   offer the graded scenario back.
4. **Two tracks in the target list** (AAAI/DOL): a high-volume *community/warm* track and a
   smaller *DUA / non-public* track, honestly flagged as human-gated and slower.
5. **This is a human-run runbook + machinery**, not auto-executed outreach (DOL/AAAI honesty).
