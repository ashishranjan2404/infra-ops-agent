# C7 — Honest Critique

## What is genuinely established
A real cross-type transfer result: a safety rule-set synthesized on the **simple** family
(seeing zero cascade labels) generalizes to the **cascade** family with a **0.078** accuracy gap
(0.923 → 0.845) and a cascade **false-allow rate of 0.066** — i.e. it recovers the general
`treats_forbidden_category → block` pattern and transfers it across incident types. Leakage-clean,
reproducible from the saved rule-set.

## Where a reviewer attacks, and my honest answer
- **"You swapped the operator from haiku to gpt-5.5 — not the paper's model."** Forced: Anthropic
  is out of credits (`400` on first run). The swap is a runtime monkeypatch, documented, no core
  edit. The synthesis machinery, interpreter, reward, and scoring are all unchanged and
  provider-independent — only the *rule-proposer* differs. A reviewer should read this as "the
  AutoHarness mechanism transfers cross-type with a competent operator," not as a model comparison.
- **"deepseek/gemini gave you nothing — cherry-picked gpt-5.5."** Honest framing: I report the
  full operator table (07). Two of three gateway models fail to emit valid rules on the full
  prompt; gpt-5.5 is the one that works. That is an operator-reliability fact, surfaced, not hidden.
  The transfer claim is about the *harness* given a working operator.
- **"Accuracy across families with different base rates is misleading."** Anticipated (grill B1):
  per-family block rate (0.506 simple vs 0.373 cascade) and the full confusion matrix are reported.
  The safety metric (cascade false-allow rate) is surfaced separately, per PSRE's demand.
- **"The synthesized harness over-blocks (37 false-blocks on cascade)."** True and stated. It is
  conservative on unseen cascade actions — arguably the *right* failure mode for a safety gate
  (false-block = unnecessary escalation; false-allow = a dangerous action through). The reward
  weights false-allows 2×, which produced this conservatism by design.
- **"`synthesis_cost` could be noise."** It's a single-seed point estimate (seed 0, budget 8).
  Multi-seed CIs would strengthen it; not run due to the ~15-min compute cap and per-call operator
  latency. Flagged as a limitation.

## Weaknesses / what's missing
1. **Single seed, budget 8.** No confidence interval on the 0.078 gap. The node-score trajectory
   (`[0.328,0.903,0.903,0.866,0.328,0.906,0.931,0.931]`) shows the search did climb and converge,
   but a multi-seed sweep would quantify variance.
2. **Operator dependence.** The result holds for gpt-5.5; with a weaker/empty-returning operator
   the harness degenerates to the seed (allow-all, false-allow 1.0). The transfer claim is
   conditional on a competent proposer.
3. **The `trap_action` ceiling.** Some cascade hazards are target-specific and not expressible in
   the general features — neither the synthesized rule nor a feature-only oracle can block them.
   This caps achievable cross-type transfer below 1.0 and is the most interesting negative finding.

## Net honest assessment
A clean, real positive result with a small, well-characterized transfer gap and an honestly
reported ceiling — conditional on (a) a working LLM operator (gpt-5.5; default haiku was out of
credits) and (b) a single seed. The apparatus and the oracle baseline are independently validated.
