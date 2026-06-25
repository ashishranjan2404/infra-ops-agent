# A3 — Honest critique

## The central limitation
A3 asks to *source 10+ fully real incidents*. The honest outcome: **zero incidents are
actually in hand.** An autonomous agent cannot send cold emails, sit on a call, or sign a
data-use agreement. What was delivered is the *complete, validated machinery* to run the
campaign — target list, sendable templates, an enforced intake schema, a consent/DUA gate,
and a tracker — plus one worked example incident. That is real and useful, but a reviewer is
right to note it is **infrastructure, not results**. The actual 10+ incidents depend on human
execution and external willingness.

## Where a reviewer attacks
1. **"This is the same as your 19 public postmortems."** Partial defense: the `provenance`
   enum + DUA track specifically target `first_party_nonpublic` material. But until a real DUA
   yields a real unpublished incident, the *novelty* is only demonstrated by one synthetic
   example (`acme_redis...`), which I authored — so it is illustrative, not evidence of yield.
2. **"Yield assumptions are hand-waved."** The funnel math (~30 contacted → 10+ usable) is a
   plausible estimate, not measured. Community donations skew toward already-public stories,
   so the *non-public* count could realistically be 0-2, not the implied several.
3. **"Evidence authoring is the hidden hard part."** The intake captures labels, but turning a
   donor's paragraph into a runnable scenario (synthetic k8s_pods/metrics/traces consistent
   with the root cause) is substantial human work the schema does not solve. I flagged this
   (Ouroboros A) but did not build the transform.
4. **Legal naivety risk.** The DUA term sheet is explicitly "not legal advice." A real
   campaign needs counsel; shipping templates that solicit incident data carries reputational
   risk if mishandled.

## What's weak / missing
- No transform script `intake → specs/real/*.json` (only the mapping table). A next task could
  build and test it against the example.
- The example is a single category (`saturation`); no breadth across the 8 categories.
- No measurement of actual response rates (impossible here).

## Net assessment
status = **completed** under the brief's rule (real plan+spec+artifacts+passing tests), with
an honest, prominent blocker: the outreach itself and any signed DUA are human/legal actions
the agent cannot perform, so the 10+ real incidents are *enabled but not yet obtained.*
