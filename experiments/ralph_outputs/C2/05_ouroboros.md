# C2 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the interpreter contract" reviewer
**Problems found:**
- A1. The `propose()` wrapper mutates module global `hs.MODEL`. If `thompson_search`
  ever parallelizes proposals, the save/restore is racy. **Resolution:** search is
  sequential (budget 8, single thread) — safe here; documented as a known limitation,
  not fixed (would require editing shared core, which is forbidden).
- A2. Rules from a *different* LLM could reference an unknown feature. **Resolution:**
  non-issue — `validate_ruleset` (reused) drops any condition whose feature ∉ FEATURES,
  and `_rule_matches` fails safe on unknown features. The interpreter is robust by design.
- A3. What if `propose` returns `[]` every round (no improving rule)? Then best == empty
  seed and the comparison degenerates. **Resolution:** handle/report explicitly — the
  script prints "(empty)" and the JSON still records it; that itself would be a finding.

## Engineer B — "the experiment validity" reviewer
**Problems found:**
- B1. **Confound:** baseline used Haiku, this uses deepseek. A rule-count or wording
  difference is not attributable to the split. **Resolution:** already in the plan — report
  hazard coverage (split-driven) separately from rule count/wording (model-driven caveat).
  This is the single most important honesty fix and it's baked into compare.md.
- B2. The held-out cascade set was chosen by hand (the 6 hand-authored cascades). Is that
  a fair test or did I cherry-pick easy ones? **Resolution:** the 6 are exactly the
  human-curated cascades with rich red-herrings (harder, not easier). I report their
  hazard coverage so the reader sees they span trap_action + treats_forbidden_category +
  rollback_no_deploy — representative, not cherry-picked-easy.
- B3. n=1. **Resolution:** report node scores; frame conclusion as structural. Stated.

## Engineer C — "the over/under-engineering" reviewer
**Problems found:**
- C1. **Over-engineering risk:** I could have re-implemented synthesis. I did NOT — I
  import the baseline machinery so the comparison is apples-to-apples and the artifact is
  small. Good.
- C2. **Under-engineering risk:** does the script actually *compute the comparison*, or
  just dump a second run and leave the diff to prose? Current script dumps cascade-synth
  numbers + hazard coverage but the *cross-run* comparison (vs baseline rex/runs file)
  lives only in compare.md. **Resolution:** acceptable — the baseline JSON already exists
  on disk; compare.md does the structured diff with real numbers pulled from both files.
  I will make compare.md cite concrete hazard-coverage from both files, not hand-wave.
- C3. The success criterion "different rules?" could be answered trivially "yes, the JSON
  differs." **Resolution:** I answer it at the hazard level (the meaningful sense) AND note
  the trivial sense, so the reader isn't misled.

## Final filtered spec deltas
- Keep import-based design (no core edits).
- compare.md MUST cite hazard coverage numbers from BOTH cascade_synth.json and
  rex/runs/harness_synth.json, and the held-out FA-rate of cascade-synth vs hand-written.
- Report empty-rule-set degenerate case if it occurs.
- Explicit model confound + n=1 caveats in compare.md and 09_critique.md.
