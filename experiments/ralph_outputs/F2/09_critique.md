# F2 — 09 Critique (honest)

## What a reviewer attacks
1. **The checker is shallow.** `check_limitations.py` proves cited files *exist*, not
   that the prose numbers match their sources. I spot-checked three load-bearing
   numbers (92.9%, the reward weights, the glob count) but did not mechanically
   verify all ~14 anchor facts. A determined reviewer could find a transcription
   slip I missed. The right fix is a number-extraction harness that greps each
   claimed figure from its source; I judged that over-engineering for a doc task.

2. **L1's two incident counts (42 vs 51) invite a "which is it?" jab.** I disclosed
   both (42 evaluated set, 51 on disk) rather than picking one, which is honest but
   slightly awkward. The underlying source-of-truth ambiguity is in the repo itself
   (FINAL_SUMMARY says 42; the directory has 51), not something I can resolve from a
   doc task. Disclosing both is the least-wrong choice but a reviewer may want the
   discrepancy explained, which I cannot fully do.

3. **Is a candid Limitations section self-sabotage?** L4 (reward hacking) and L5
   (blocked transfer) are damaging admissions. I mitigated with the `### Scope`
   closer naming the two surviving results, but a hostile reviewer could quote L4 in
   isolation. This is an inherent tension in honest limitations writing; I chose
   candor per the task mandate, accepting the rhetorical cost.

## What's genuinely weak in the underlying work (not just my section)
- The strongest positive result (harness synthesis) and the RFT result live in
  *different* parts of the pipeline; the paper's narrative coherence is thinner than
  the section implies.
- "REx-with-SME 2.8×" leans on author-written corrections (semi-synthetic), so even
  the surviving Scope result is evaluation-relative. I flagged this in L2/L6 but the
  Scope closer states it more confidently than the caveats warrant. A careful reader
  will notice the Scope paragraph and L6 are in mild tension.

## What's missing
- No comparison of *our* limitations against the comparable benchmarks (SREGym,
  AIOpsLab) — a related-work-style honesty contrast would strengthen credibility.
- No quantification of "how synthetic is too synthetic" — e.g., a held-out real
  incident even as an anecdote would materially de-risk L1. None was available.

## Honest status
The deliverable is real, grounded, and tested, but it is a *documentation* artifact:
its value is candor and traceability, not new experimental evidence. It faithfully
reports negative/blocked results (declining v1 RFT, blocked Fireball, gameable
judge) rather than hiding them.
