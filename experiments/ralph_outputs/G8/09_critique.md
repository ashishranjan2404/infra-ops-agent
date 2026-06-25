# 09 — Critique (honest)

## What a reviewer will attack
1. **The competitive inputs (G5/G6/G7) were empty.** The task says "synthesize G5/G6/G7," and
   those step files did not exist at run time. I substituted the underlying verified repo
   artifacts. A strict reviewer can say the synthesis isn't *of the competitive analysis* but
   *of the product's own claims*. Honest framing: this is a "why we're different" pitch grounded
   in real results; it is not a head-to-head feature matrix against named competitors, because no
   competitor data was available in-repo. If G5/G6/G7 later produce named-competitor analysis, the
   one-pager's "incumbent contrast" line should be upgraded with specifics.
2. **No named competitors.** The doc contrasts against a generic "incumbent eval harness that
   grades resolution." That's true and defensible but soft. A partner may ask "who specifically?"
   We deliberately avoided naming firms we have no analysis of, to stay honest — but it weakens
   the "different from *whom*" punch.
3. **Absolute scores are low** (best model ~0.50 one-shot). We frame this as "hard and
   discriminative by design," which is the correct benchmark argument, but a non-technical
   investor may still read 0.50 as weak. Risk of misread despite honest intent.
4. **Contamination is real and admitted, not solved.** We defend by "grading the mechanism," but
   we have not *measured* a contamination gap (e.g., memorized vs novel incident performance
   delta). The defense is argued, not yet quantified. That's a genuine open gap.
5. **The live-GKE claim leans on the status table**, not a re-verified run in this session. I did
   not re-deploy or re-probe the cluster (out of scope, and MEMORY says keep it untouched). If
   the cluster were down, "runs on a live GKE call-mesh" would be stale.

## What's weak / missing
- No quantified contamination control (the most rigorous next artifact).
- No dollar/ROI framing for the investor ask — deliberately omitted (no real data), but a partner
  pitch usually wants it.
- The "ask" is generic; a real raise/partnership pitch would tailor it.

## What's genuinely strong
- Every number is auditable against a repo file — rare for a pitch doc.
- It leads with, rather than hides, the unflattering ablation — which is both honest and, against
  demo-ware competitors, a real differentiator.
- The wedge (grade the mechanism + the trap, model-frozen, one command) is accurate to the code.

## Honest status
Deliverable is complete and real. The main caveat is the sourcing substitution (empty G5/G6/G7)
and the absence of named-competitor data — documented, not hidden.
