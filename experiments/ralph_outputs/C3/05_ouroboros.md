# C3 — 05 Ouroboros (3 self-critiques of the spec)

## Engineer A — "the leakage is subtler than your assert"
**Problem found:** T1/T2 only check `TRAIN ∩ HELDOUT = ∅` by *id*. But
`thompson_search`'s `evaluate=train_score` closes over `train_ex` — good — yet
`_propose` also closes over `train_ex` and shows the model the train false-allow/-block
examples in its prompt. If I had accidentally passed `held_ex` into either closure, the
id-level disjointness assert would still pass while held-out labels leaked into search.
**Fix:** the spec/code must make it textually obvious that BOTH `propose` and `evaluate`
take *only* `train_ex`, and the leakage line must assert that, not just id-disjointness.
→ Verified in code: both closures use `train_ex`; held-out is touched only in the final
scoring pass after `best` is fixed. Documented explicitly in 08.

## Engineer B — "your headline metric can be gamed by the empty rule-set"
**Problem found:** On a split where most examples are `should_block=False`, an *empty*
rule-set (allow-all) gets high accuracy and FA% looks fine only if few blockables exist.
If I report just "94% held-out," a reviewer can't tell if that beats the trivial
baseline. **Fix:** always report the **seed (empty)** harness in the same table. Here
seed gets 0.500 held-out accuracy and **1.0 false-allow rate** (it allows every unsafe
action) — so the synthesized 0.941 / 0.059 is a real lift over trivial, not an artifact
of class imbalance. Already in the spec's `table`; made load-bearing in 08.

## Engineer C — "the split is hand-picked; show me it isn't reverse-engineered"
**Problem found:** I chose TRAIN/HELDOUT so `treats_forbidden_category` spans both. A
skeptic says: did you pick the split *after* seeing which split makes synthesis look
good? **Fix:** the split criterion is stated *mechanistically and a priori* — "the
GENERALIZABLE hazard must appear in both splits; single-incident hazards
(`leak_restart`) go to held-out and are reported out-of-scope." That criterion is
independent of synthesis output. To prove robustness I also note the *failure* it
produces: putting `media_oom_leak` (the leak) in HELDOUT guarantees 2 held-out
false-allows the synthesized rule structurally cannot fix — i.e., the split was NOT
chosen to flatter the result. Documented as an honest negative in 09.

## Final filtered spec
Spec unchanged in structure; three clarifications baked in:
(1) leakage claim is about *closure inputs*, not just id-disjointness;
(2) the empty-seed row is mandatory as the triviality floor;
(3) the split criterion is a-priori and is shown to *cost* held-out accuracy, not buy it.
