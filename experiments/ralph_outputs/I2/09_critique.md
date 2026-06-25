# I2 — 09 Critique (honest)

## What's weak
1. **"Bimodality" on a two-atom support is almost definitional.** Once you
   condition on the competent event, R can only take two values, so calling it
   "bimodal" is true but not deep. The non-trivial content is the *threshold*
   (`TRAP_PENALTY > W_RESOLVED` nullifies the resolved reward), not the existence
   of two modes. A reviewer could say the headline oversells.
2. **The interesting (full) population is multi-modal, not bimodal.** The clean
   bimodal result requires conditioning. In a real GRPO group the plans are NOT
   all competent, so the *empirical* group-reward histogram is 4–5 modes, with a
   dominant spike at 0 (trap basin + total failures collapse together). So "the
   reward distribution is bimodal" is an over-simplification of the real training
   signal; what's truly bimodal is the *competent* slice.
3. **Synthetic, not measured.** Draws come from a hand-set `Population`, not from
   real agent rollouts on the CIDG scenarios. The theorem is coupling-free
   (conditioned), so this doesn't threaten correctness, but it means the *full*
   histogram shape (mass fractions) is illustrative, not empirical.
4. **Sarle's BC is uninformative here** (≈0.32 < 0.555 throughout) because
   kurtosis on a two-atom support is small; reporting it at all invites a "your
   own metric says unimodal" jab, even though we explicitly de-gate it.
5. **Clamp-to-0 caveat is real but unaddressed in core.** For TRAP_PENALTY≥1.0 all
   trap basins collapse to 0, erasing degree-of-badness gradient. The shipped 0.60
   already clamps total failures into the same 0 bin as trapped-competent-but-
   below-zero plans — the basin atom 0.40 is fine, but failure+trap combos sit at
   0 alongside pure failures, muddying the low mode.

## What a reviewer attacks first
- "You proved a two-point distribution is bimodal — so what?" → Rebuttal: the
  deliverable is the *threshold characterization* (nullification iff
  `tp ≥ W_RESOLVED`) plus the demonstration that the SHIPPED penalty sits above
  it, which is the design-relevant claim, not the modality per se.
- "Show it on real rollouts." → Fair; this is a blocker noted below.

## Missing / blocked
- **Real rollout reward histogram** on `scenarios/cidg/generated/*.yaml` via
  `rex/eval_pass_at_k.py` would make the full-population shape empirical rather
  than synthetic. Not run here (would need a live LLM policy + budget); the
  conditioned theorem stands without it. This is the honest gap.

## Net
The proof and threshold characterization are correct, reproducible, and match the
shipped constants. The weakness is depth (two-atom bimodality is easy) and that the
*full* training-time distribution is multi-modal — both stated openly rather than
papered over.
