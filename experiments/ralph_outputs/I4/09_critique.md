# I4 — Critique (honest)

## What a reviewer attacks
1. **"This is a descriptive statistic dressed as information theory."** Fair, partly. The
   entropies are empirical over a hand-built 42-scenario corpus (A5). There is no PAC bound,
   no worst-case theorem. The IT vocabulary (`H`, `IG`, `I(y;R4|R123)`) is *correctly applied*
   but the claim's force is "on this realized data", which a theorist will discount. Defence:
   the doc says so loudly (§7, §8) and the *real* theorem (3 mechanism classes) lives in C12's
   Lemma 1, which I compose with rather than re-prove.

2. **"The Φ-split is where you win the argument."** The biggest soft spot. By scoping to the
   Φ-expressible region I exclude the 35 topology traps — exactly the cases where the rules
   FAIL — and then report 95.5%. A hostile reviewer calls this cherry-picking. Defence: the
   split is *named and quantified* (35 oos positives printed every run), and the entire §6b is
   devoted to it; the headline is explicitly "over Φ", not "universal". But the honest reading
   is: **3 rules are sufficient only because we agreed not to ask them to see topology.**

3. **"The MI bound is loose."** `I(y;R4|R123) ≤ 0.0344` is achieved only by the degenerate
   full-vector partition, not a real rule. So the *true* gain of a writable 4th rule is likely
   far below 0.0344 — which actually *strengthens* "3 rules suffice", but a reviewer could
   equally say the bound is too loose to be informative. It is informative precisely because it
   is small.

4. **"Entropy can't tell a safe rule from a confidently-wrong one."** True and conceded (§8.4).
   The coverage metric and C12's accuracy witness carry the safety burden; the entropy alone
   would be a dangerous thing to optimize.

## What is genuinely weak / blocked
- **No generalization claim.** I cannot, from this corpus, say a *new* incident family won't
  introduce a 4th mechanism. C12's held-out evidence (`harness_synth` TRAIN/HELDOUT) is
  supportive but I did not extend it; I only measured bits on the union.
- **The 0.0344 residual is real and unclosed.** I did not implement the 7th feature that would
  close it — correctly, since that is a shared-core change out of scope, but it means the
  argument ends at "≥95%", not "100%".
- **Corpus dependence.** If the generated registry's mix of cascade traps changes, `H(y)` and
  the coverage move. The *shape* of the result (R1 dominates, 3 rules near-floor) is robust,
  but the exact 95.5% is corpus-specific.

## What's missing
- A sensitivity check: how do the entropies move if the corpus reweights simple vs cascade?
  (Not run — would strengthen the robustness claim.)
- A direct comparison of `I(y;R4|R123)` for *named* candidate 4th rules (e.g. a tool-keyed
  rollback refinement) vs the full-vector ceiling. The ceiling is computed; the specific
  realizations are not.

## Honest bottom line
The deliverable is a *correct, reproducible, honestly-scoped* information-theoretic
measurement that **upgrades C12's asserted §6 into a measured result** — and in doing so
finds C12 mildly overclaimed (0.0344 bits ≠ 0). Its main vulnerability is the Φ-split, which
is disclosed but is still the move that makes "3 suffice" true. Read it as: *given the harness's
own six features, three rules extract ~95% of all the label information those features contain,
and a fourth is worth ≤3.5% — the rest of the problem is features, not rules.*
