# 05 — Ouroboros (3 self-critiques)

## Critic 1 — "Skeptical VC partner"
**Problems found:**
- "Open graduation benchmark" still reads like a category claim with no defensibility. *Who else
  can't do this?* A one-pager titled "why we're different" must name what the alternative is —
  even implicitly. Add a single contrast line: incumbents grade "did it come back up"; we grade
  the mechanism + the trap.
- C6 (haiku 0.27 vs opus 0.50) is a *low* absolute number. A VC sees 0.50 and thinks "your best
  model only scores 50%?" Must frame it as *the env is hard and discriminative* — that's the
  point of a benchmark — not as a model weakness.
- No "ask." The brief says investors/partners; a one-pager without a call-to-action is a poster.

**Fixes:** add a one-line incumbent contrast; reframe C6 as "hard + discriminative by design";
add an explicit ask block.

## Critic 2 — "Adversarial SRE evaluator"
**Problems found:**
- The trap claim needs a *concrete* example or it's abstract. "Naive fix worsens it" is jargon.
  Use the real one: scaling a crash-looping control plane herds its datastore → worse. That line
  is in `ARCHITECTURE.md`; use it verbatim-ish so it's grounded.
- "Live GKE" (C11) is a strong claim — is it real? Per `ARCHITECTURE.md` status table it's
  "deployed + verified on live GKE" and MEMORY notes the cluster is kept alive. OK to claim, but
  phrase as "runs on a live GKE call-mesh" not "production." Don't overstate.
- C5 "0.90 vs 0.95 hand-written" — a critic notes we are *worse* than hand-written. Must frame as
  "auto-discovered, generalizes to unseen, at 95% of hand-tuned with a fraction of the rules
  (3 vs 14)." The compression + generalization is the win, not raw accuracy.

**Fixes:** use the concrete control-plane trap example; soften "GKE" wording; reframe C5 around
compression + generalization.

## Critic 3 — "Honesty auditor"
**Problems found:**
- Is the honest-caveat block going to be read as us *admitting the product doesn't work*? Risk.
  It must be framed as "we ran the fair control ourselves and moved our claims to what survives"
  — that's a *credibility* signal, not a confession. Wording matters.
- C7 vs C9 tension: page says "small+REx beats big zero-shot" (C7) AND "REx lift was mostly
  leakage" (C9). A careful reader sees a contradiction. Resolve it: C7 is easy-tier and the
  *honest* REx value is the **escalation/safety behavior** + the **hard-tier ~triple via
  escalation** (C8), not the easy-tier number. Make the page state this resolution explicitly so
  it's not self-contradictory.
- Word budget: with all additions, risk of blowing past one page. Cut adjectives, keep numbers.

**Fixes:** frame caveat as "we ran the fair control"; explicitly resolve C7/C9 by anchoring REx's
honest value on escalation + hard-tier; hard word cap < 800.

## Final filtered spec (what the one-pager will do)
1. Lead with thesis + one incumbent-contrast line.
2. Wedge: open graduation benchmark (qualified) + trap safety, with the concrete control-plane
   trap example.
3. Moat: verifiable env, learned verifier (compression + generalization framing), two-tier
   fidelity (sim + live GKE call-mesh), model-frozen / one-command.
4. Proof: C1,C2 (scale), C4/C6 (discriminative spread), C5 (verifier generalizes), C8 (hard-tier
   honest REx via escalation).
5. Honesty block: "we ran the fair control and moved our claims" + the C7/C9 resolution.
6. Ask.
Word cap < 800.
