# E7 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI
Reviewer · **RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial takes
- **SMR:** Transfer claims need a *negative control*. If TextWorld scores high
  just because the deterministic judge is lexical, that's not transfer of the
  policy, it's leakage of the gold string into the answer. Want a shuffled-gold
  baseline.
- **PSRE:** The whole premise is that incident response and Zork are the same
  MDP. They're not operationally — in IF you can save/restore and brute-force;
  incidents are irreversible. The adapter must not let "transfer works in games"
  imply "transfer works in prod."
- **AAAI:** Survey-only contributions get desk-rejected. What's the *measurable*
  hypothesis? Define the transfer metric before building the adapter.
- **RLE:** Per-step `available_actions` differ wildly: Jericho's `valid_actions`
  is a world-model *handicap* not present at real inference; TextWorld's
  `admissible_commands` is similar. If you train on those you over-fit to an
  oracle that vanishes in deployment. Flag it in the schema.
- **DVO:** Where does the data come from? No internet here. If you "download
  Jericho ROMs" you'll fabricate. Be explicit: synthetic fixtures now, real
  loaders behind a documented blocker.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** Disagree that a shuffled-gold control is enough. Lexical judge
  passing on shuffled gold tests the *judge*, not *transfer*. The real control is
  **cross-domain**: train/select on SRE, evaluate zero-shot on TextWorld vs a
  TextWorld-native baseline. A within-domain shuffle won't catch domain leakage.
- **PSRE → AAAI:** I think the reviewer is over-indexing on a single headline
  metric. Operationally the useful artifact is the *adapter contract*, not a
  number. If you force one metric too early you'll pick game-score, which PSRE
  considers misleading for the SRE story. Keep the metric plural.
- **AAAI → DVO:** Synthetic fixtures are fine for a *unit test* but are NOT
  evidence of transfer. I'll reject any claim that says "transfer demonstrated"
  off synthetic data. The fixture proves *plumbing*, full stop — say exactly that.
- **SMR → RLE:** Agree the `valid_actions` handicap is real, but don't strip it
  from the schema — record it as `available_actions` and let the experiment
  *ablate* it. Removing it loses the ability to study its effect.
- **DVO → PSRE:** Push back: irreversibility doesn't break the adapter; it's a
  *property of the reward*, not the trajectory shape. The adapter is shape-only.
  Reversibility belongs in the experiment plan's caveats, not the schema.

## Round 3 — synthesis
Consensus that survived disagreement:
1. **Scope the claim honestly:** the deliverable proves *plumbing + a runnable
   transfer protocol*, not transfer itself (synthetic data ≠ evidence). (AAAI, DVO)
2. **Real control is cross-domain zero-shot**, not within-domain shuffle. Plan
   must specify: select policy on SRE → eval on game domain vs native baseline. (RLE, SMR)
3. **Keep `available_actions` in schema**, but the plan must ablate the oracle
   handicap and report both. (SMR vs RLE resolved)
4. **Reversibility / irreversibility** is a documented caveat in the plan, kept
   out of the shape schema. (DVO vs PSRE resolved)
5. **Plural metrics:** episode-success, judge-score, action-overlap with gold,
   normalized game-score — not one headline. (PSRE vs AAAI resolved)
