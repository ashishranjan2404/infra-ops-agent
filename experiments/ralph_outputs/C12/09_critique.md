# C12 — Step 9: Honest Critique

## What a reviewer will attack

1. **"You proved a tautology."** Lemma 1 partitions the hazards into 3 classes — but the
   3 rules were *defined* as those 3 classes, so the partition is by construction.
   Rebuttal: Lemma 1's content is not the naming but the *enumeration* — it shows the
   `ground_truth` branch set has no 4th Φ-expressible mechanism. Still, a hostile
   reviewer can call this "definitional," and they have a point: the real work is the
   feature space, not the rule count.

2. **The headline claim is empirically FALSE on the full corpus.** The verifier returns
   FAIL (39/580). We rescue it by restricting to the "feature-expressible subset," which
   is a scope-narrowing the reader could call special-pleading. We mitigate by reporting
   the FAIL prominently and attributing it to a missing *feature*, but a skeptic may say
   "then 3 rules do NOT suffice, full stop." That is a fair reading of the raw result.

3. **R3 is 3 conditions dressed as 1.** Counting 3 schemas when the interpreter sees 5
   conjunctions is a soft fudge. We disclose both numbers, but the clean "3" depends on
   the mechanism story, not the implementation.

4. **The information-theoretic statement is over a fixed, tiny realized set.** `I(y;R₄|c)=0`
   is true on V but says nothing about unseen incidents. The doc admits this (A5, Limit
   3) but the *phrase* "information-theoretically complete" oversells to a casual reader.

5. **No concurrency coverage.** Real "the fix made it worse" incidents are often
   multi-action (scale + restart together). A3 assumes single-action gating, so the
   whole analysis sidesteps arguably the most dangerous trap class. This is a real gap,
   not just a formality.

## What's weak / what I'd fix with more time
- Add the 7th feature (`targets_victim_not_root`, i.e. topology distance) and re-run the
  verifier to test whether Lemma 1's 3-class structure *re-closes* around it — that
  would turn the negative result into a constructive "3 rules per feature-layer" claim.
- Fix the rollback collision by splitting `b₅` into `rollback_no_deploy_event` vs
  `rollback_targets_bad_content`; check whether that restores 100% on the subset.
- The proof would be stronger as a VC-dimension calculation of the
  "≤3 conjunctive rules over Φ" class with a sample-complexity bound — currently we only
  do empirical risk, not a generalization bound.

## Honest verdict
This is a **partial success**: a genuinely-proven sub-result (3 mechanism classes
saturate the fixed feature space) plus an honest empirical witness that *disproves* the
naive universal claim and precisely locates the boundary (it's the feature set, not the
rule count). The deliverable is real, runnable, and reproducible. It is NOT a clean
"3 rules are universally sufficient" theorem, and the document says so.
