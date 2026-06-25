# C12 — Step 5: Ouroboros (self-critique as 3 engineers)

## Engineer 1 — Formal-methods skeptic
**Problems found:**
- (P1) The theorem as stated in 04 is *vacuously* defendable: it ends with "PROVIDED no
  explicit trap_action escapes the 3 rules." If that proviso fails the theorem says
  nothing. The doc must make the proviso a **checked premise** and report the check, or
  the theorem is unfalsifiable.
- (P2) `H(y|c)=0` is asserted; but `c` is defined FROM the rules, so "rules separate ⇒
  H=0" is circular unless `c` is shown well-defined (rules can fire simultaneously).
  Need a tie-break / disjunction note: multiple rules firing is fine because all firing
  rules vote block=1; define `c` as the *lowest-index* firing rule.

## Engineer 2 — Adversarial-substrate engineer
**Problems found:**
- (P3) The generated registry (`scenarios/cidg/generated/registry.json`) is merged into
  `_SCENARIOS` at import. If it contains a scenario whose `trap_actions` uses a tool with
  NO entry in `TOOL_TREATS` and NO state flag, ground_truth labels it `trap_action`
  (block) but ALL three rules see an all-false feature vector → predicted allow →
  MISCLASSIFY. The verifier MUST surface this; the proof must scope to scenarios where
  every block-label is one of the 6-feature hazards.
- (P4) "Feature collision" is the real disproof condition and 04 mentions it but the
  doc must show it was actually run and came back clean, with the N.

## Engineer 3 — Pragmatic reviewer / over-engineering watch
**Problems found:**
- (P5) Importing `is_safe_synth` drags in `agent.llm.call` at module import of
  `harness_synth` (line: `from agent.llm import call`). That can fail offline. The
  verifier should re-implement the 3-rule matcher locally (a 6-line function) and only
  import the pure-data helpers, OR import lazily and degrade gracefully.
- (P6) Over-claiming risk: calling it "proof" in the filename. Rename intent: the doc is
  titled "argument + empirical witness." Keep the word *proof* only for the
  combinatorial lemma that is genuinely proven (exhaustiveness of A/B/C is a proof;
  global separability is empirical).

## Final filtered spec (changes adopted)
- (from P1/P4) Theorem split into **Lemma 1 (Exhaustiveness, proven)** and
  **Proposition 2 (Realizability, empirically verified)** — only Lemma 1 is called a
  proof.
- (from P2) Define `c` as lowest-index firing rule; note rules are monotone (all vote
  block), so class assignment is well-defined and `H(y|c)=0` is non-circular *given*
  Prop 2.
- (from P3) Add explicit SCOPE: theorem holds over scenarios whose every positive label
  is a 6-feature hazard; verifier flags `trap_action`-only blocks that escape and the
  doc reports the count (expected: the hand-authored cascades use feature hazards; pure
  explicit traps, if any, are listed as out-of-scope residue).
- (from P5) Verifier re-implements the matcher locally; imports only
  `load_scenario`, `_SCENARIOS`, `labeled_examples` (which do not need the LLM). If even
  those fail, it degrades to a self-contained synthetic label table and says so.
- (from P6) Filename stays `three_rules_proof.md` (task asked for a "proof doc") but the
  H1 and abstract explicitly say "argument backed by an empirical witness; only the
  exhaustiveness lemma is a closed proof."
