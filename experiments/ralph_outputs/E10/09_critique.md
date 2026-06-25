# E10 — Honest critique

## What's genuinely strong
- The section is reviewer-ready prose, grounded in real repo objects, with a clean
  pre-registration. The frozen-vs-fine-tuned reconciliation (the one real internal-consistency
  risk in the paper) is addressed head-on.
- The anti-fabrication discipline is enforced *mechanically* (validator), not just promised.

## What's weak / what a reviewer attacks
1. **It's a section with no results.** The honest core: E10 was always a *writing* task whose
   *subject* (C2 transfer) is empirically blocked by E1/E2. A reviewer who wants the transfer
   *number* gets a pre-registration, not an answer. The section is as good as a no-data section
   can be — but it cannot manufacture the contribution the paper's title advertises ("Cross-
   Domain Transfer"). If E1/E2 never land, the paper must demote C2 from a claim to future work,
   and the title may need softening. The section says this (fallback in 5.x.5), but it's a real
   exposure, not a cosmetic one.
2. **The mechanism is conjecture, lightly tested.** "Shared state-transition inductive bias"
   is an appealing story, but it's only probed indirectly by E6 (full vs state/action-only).
   There's no representation-similarity analysis, no probing — a strong ML reviewer will note
   the mechanism is asserted more than shown. I deliberately labeled it a conjecture, which is
   honest, but it limits the section's intellectual contribution to "we measured transfer"
   rather than "we explained it."
3. **Contamination risk is real and only partly mitigated.** Cascade incidents are
   reconstructed from public post-mortems. A pretrained base may have read those incidents as
   text. The held-out-by-family novel set (E5) helps but does not fully decontaminate; apparent
   transfer could be memorized post-mortem text. I flagged this in 5.x.6 but cannot resolve it
   without the data.
4. **D&D→SRE is inherently a hard sell.** Even with positive E3 results, "Dungeons & Dragons
   improves incident response" invites skepticism. E7 (other source domains) would be the
   evidence that it's *structure*, not *D&D-specific luck* — and E7 is unrun and listed as a
   frontier item. So the most persuasive generalization evidence is exactly the part that's
   future work.
5. **Validator is shallow.** It checks structure and the no-fabrication invariant, not the
   *quality* of the argument. It cannot catch a subtly wrong claim. The real QA here was human-
   style reading, not the script.

## Blocked/negative honesty
- The deliverable (the section) is **completed**. The *experiments it describes* (E3–E9) are
  **blocked** on E1 (Fireball-trained model not pushed) and E2 (FIREBALL source corpus absent),
  exactly as `P7_fireball_status.md` and `CLAIMS_EVIDENCE.md` record. No transfer result is
  claimed. That is the correct, non-fabricated state.

## If I had more to work with
With E1/E2 unblocked I would run E3 first (headline H1), then E9 (the transfer-vs-more-data
control — without it, H1 is unconvincing), then E4 (no-harm). Those three convert the section
from a protocol into a result. Everything needed to do that is already in the repo.
