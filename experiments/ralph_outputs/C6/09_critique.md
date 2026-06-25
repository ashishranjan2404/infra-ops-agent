# C6 — 09 Critique (honest)

## What a reviewer attacks
1. **Single seed, n=3 held-out, n=1 run per proposer.** This is a case study, not a
   benchmark. The Thompson budget is 8 and the proposers are reasoning models that
   ignore temperature, so a re-run could shift `best_train_score` and even the chosen
   rule-set. The deepseek "empty rule-set" might partly be unlucky sampling, not pure
   incompetence — though 8/8 nodes at the seed score makes consistent failure likely.
   **Honest stance:** results are *suggestive and directional*, not statistically
   significant. The driver is seed-parameterized so a multi-seed sweep is a one-liner;
   I did not run it under the 15-min cap.

2. **The intended proposer (claude-haiku-4-5) never ran** — Anthropic credits exhausted.
   So the headline "proposer matters" is demonstrated on SUBSTITUTE proposers, not on
   the model the harness was tuned for (`MODEL = "claude-haiku-4-5"`, `_SCHEMA` prose
   written with haiku in mind). It's plausible the prompt is haiku-shaped and
   handicaps deepseek specifically. I cannot rule this out.

3. **Cross-provider apples-to-oranges.** Per `agent/llm.py`, Fireworks (minimax) has no
   system role and gateway models drop temperature; prompt delivery differs by provider.
   Some of the gap between minimax and deepseek could be prompt-formatting, not
   reasoning quality.

4. **Budget confound.** A proposer that emits the right rule early can beat one that
   emits it late purely from the 8-node budget. minimax found its 0.781 rule-set at
   node 2; gpt-5.5 only reached 0.798 at node 7. The ranking partly reflects *when*,
   not just *whether*, a good rule appears.

5. **No tree-topology record.** I store `node_scores` but not parent links, so I can't
   show whether a proposer improved monotonically vs got one lucky seed-child. Known
   limitation, not re-plumbed under cap.

## What's genuinely weak / blocked
- The deepseek empty-set result is the most fragile claim — it's the one most likely to
  be sampling/prompt-fit rather than a stable property. I report it but flag it.
- No confidence intervals. By design (compute cap), not oversight; called out, not faked.

## What's solid
- The mechanism is real and surgical: proposer is the only varied factor; evaluator is
  provably deterministic (T3); the spread in held-out FA/FB is large and traces directly
  to the actual synthesized rules, so SOME real proposer effect exists even if exact
  rankings are noisy.
- No core files touched; fully reproducible from the driver.
