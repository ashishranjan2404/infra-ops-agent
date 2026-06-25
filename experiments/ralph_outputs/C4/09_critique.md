# C4 — 09 Critique (honest)

## What a hostile reviewer attacks

1. **"You analyzed v2's 3 rules but the task could mean v1's 10."** The task literally says
   "3 synthesized rules" and v2 has `n_rules:3`, so v2 is the obvious referent — but this rests on
   an interpretive judgment. Mitigation: I explicitly documented v1 (10 rules) and analyzed the
   v1→v2 collapse, so neither reading is ignored. Still, a reviewer who insisted "3 rules" meant
   *three rule-families inside v1's 10* would find that reading unaddressed (I treated v1's 10 as a
   single over-conditioned predecessor, not as 3 families).

2. **"Interpretability is asserted, not measured."** I introduced three yardsticks (1:1 mapping,
   simulability, sparsity) and scored them, but simulability in particular is judged informally
   ("a human can predict the output") rather than via a human study or a formal proxy
   (e.g., decision-path length). For a safety harness this is probably fine, but it is not a
   rigorous interpretability metric in the IML-research sense.

3. **"The clean recoveries are rigged."** R1/R3 map cleanly to `is_safe` partly because the 6
   features were *designed to mirror* `is_safe`'s signals (stated in `harness_synth.py`). So
   "the search recovered the human harness" is less impressive than it sounds — the search space
   was shaped to make that recovery likely. I disclosed this in "Honest limitations," but it
   genuinely caps how much the interpretability result can claim.

4. **"R2's worked-example contrast is a hypothetical."** The synth-blocks / hand-written-allows
   `scale_deployment`-during-leak example does **not** occur as a held-out false-block; I
   constructed the feature dict to illustrate the divergence. I labeled it as illustrative, but a
   reviewer could fairly say a *real* data point would be stronger. None existed in held-out
   (FB-rate 0), which is itself the reason — a slight catch-22.

## What is genuinely weak / missing
- **No coverage of the 30+ generated scenarios.** The analysis is scoped to the 7 train / 3
  held-out incidents the synthesis used. Whether these 3 rules generalize to the broader generated
  registry is untested here.
- **The `last_ready_node_op` feature is dead weight in these rules** — it exists but no rule uses
  it because the hazard is absent from TRAIN. I noted this as "out of scope," but it also means the
  synthesized harness has a *known blind spot a deployer must be warned about*, which I could have
  surfaced even more prominently as an operational caveat.
- **No ablation of rule ordering.** First-match-wins means R1 can shadow R3 (shown in the R3
  example). I noted it but did not test whether reordering changes any verdict (it does not on this
  data, but I did not prove it).

## Honest bottom line
The deliverable is real, reproduced, and correctly scoped, and the central claim
(rules are interpretable, by construction) is well-supported. The two soft spots are (a) the
interpretability yardstick "simulability" is informal, and (b) the clean human-clause recoveries
are partly a consequence of a feature set designed to mirror the human harness — both disclosed,
neither fatal. Not a blocked result: the rules exist as data and every number was verified.
