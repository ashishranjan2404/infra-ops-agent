# F12 — 09 Critique (honest)

## What a sharp investor / diligence partner will attack
1. **All evidence is in-sim (plus one live cluster), not in production.** 0.23 → 0.90 is on our
   own simulator and a live GKE copy — not on a customer's real incidents. The memo is careful
   ("faithful simulator", "physically real cascades"), but a skeptic will (correctly) say the
   number is on a benchmark we built and grade. That is the single biggest gap. The memo's wedge
   (selling the benchmark itself) partly turns this into the product, but it doesn't erase the
   "graded on your own homework" critique.
2. **Only two models tested.** "Works with any model" is supported by two (glm-5p2,
   deepseek-v4-pro), not a broad sweep. The memo says "two different models," which is honest,
   but the implied generality is ahead of the data.
3. **The honest negative is real and load-bearing.** rex_no_oracle ≈ baseline means the lift is
   the feedback content, not the search. If that feedback's quality doesn't generalize to
   messy real incidents, the whole result could shrink. The memo frames this well but cannot
   prove it generalizes.
4. **No traction.** Zero customers, revenue, or LOIs. The memo correctly avoids fabricating any,
   but that means the doc is a research-strength-only pitch. For some YC partners that's fine
   (pre-seed); for others it's a pass.
5. **Market section is thin and partly estimated.** No bottoms-up TAM, no named design partner.
   Honest, but a weak section by fundraising standards.

## What's weak in MY deliverable specifically
- A 2-pager forced me to cut the mechanism to two sentences; a technical co-founder reading it
  might want one diagram. (Out of scope here; F-series likely has a separate figure task.)
- The "~4x" framing is arithmetically true (0.897/0.230) but pass@1 is a rate, and a purist
  would prefer "from 23% to 90%" over "4x." I kept both; defensible but debatable.
- The raise size and milestone are placeholders — a real memo needs the founders to fill them.

## What I'd do next
- Add a real-incident validation number (the project has real post-mortem specs and a live
  cluster — a small "on N real post-mortems" result would blunt critique #1 hard).
- Run the multi-model frontier sweep (A1's runner supports it) to back "any model."
- Get one design-partner logo to convert this from research pitch to traction pitch.

## Bottom line
The memo is honest and every number is real, but the underlying evidence is benchmark-stage, not
production-stage. The doc is a credible *pre-seed research* pitch; it is not yet a *traction*
pitch, and it does not pretend to be.
