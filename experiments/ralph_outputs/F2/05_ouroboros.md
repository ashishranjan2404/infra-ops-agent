# F2 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the fact-checker"
**Problems found:**
- Spec says "51 generated YAMLs" but FINAL_SUMMARY says "42 total incidents (10
  original + 32 generated)." The on-disk glob count and the narrative count disagree.
  → **Real ambiguity.** Fix: state BOTH — 32 generated for the headline set, and note
  the on-disk `generated/` dir now holds 51 files (later additions). Cite the glob count
  as the disk fact, the 42 as the evaluated set. Do not silently pick one.
- L4 cap claim "0.30 of total reward" — verify against scoring weights. CLAIMS_EVIDENCE
  says diag is 30% of reward; D13 says diag hack caps at 0.30 and composed with a real
  fix reaches 0.55 (0.30 diag + 0.25 fix). → keep both numbers, they're consistent.

## Engineer B — "the scope hawk"
**Problems found:**
- The section risks reading as a confession that nullifies the paper (REV's R2 fear).
  The `Scope` subsection exists but the spec doesn't require it to actually name which
  results *survive*. → Fix: make `Scope` explicitly list the surviving results: harness
  synthesis (66.7%→89.7% accuracy, Table 3) and REx-with-SME lift (0.242→0.687, 2.8×)
  are the load-bearing positive results and are NOT undermined by L1–L6 (they're
  evaluation-relative but real within the defined oracle).
- L2 (circularity) and L1 (synthetic) overlap; a reader may see redundancy. → Fix: L1 =
  data provenance (incidents are fabricated); L2 = the *evaluator* shares authorship with
  the data (a distinct circularity). Add one sentence to L2 disambiguating from L1.

## Engineer C — "the reproducibility auditor"
**Problems found:**
- `check_limitations.py` checks file *existence* but not that the *numbers* in
  LIMITATIONS.md actually appear in the source files. That's a weaker guarantee than
  implied. → **Accepted as a known limitation of the checker**, documented in 09. Full
  number-grounding would need parsing each source; out of scope for a doc task, but I
  will at least grep one canary number (the 92.9% hedge fool-rate) from D13 in the test
  run to prove the citation is live, not invented.
- The checker hardcodes `/Users/mei/rl`. If run elsewhere it breaks. → Fix: derive repo
  root by walking up from the script to the dir containing `experiments/` and `rex/`,
  fall back to the hardcoded path.

## Final filtered spec (deltas applied)
1. L1 states 32 generated (evaluated set) AND the current `generated/` disk count; no
   silent number-picking.
2. `Scope` subsection explicitly names surviving results (Table 3 harness; REx-SME 2.8×).
3. L2 gets a disambiguating sentence vs L1.
4. `check_limitations.py` derives repo root dynamically; the 07 test run also greps the
   92.9% canary from D13 to prove citations are live.
5. Checker's existence-only guarantee is disclosed in 09 as a known weakness.
