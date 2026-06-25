# D13 — 09 Critique (honest)

## Where a reviewer attacks this
1. **The oracle is author-defined.** The fool-rate is only as credible as my
   `HUMAN_ORACLE` labels. A reviewer can reject the `homoglyph` or even the `hedge`
   label and the headline number drops. Mitigation: per-attack reporting + fool-rate-0
   guards proving the oracle isn't rigged — but it remains a judgement call, not a
   crowd-labeled gold standard. **This is the weakest point.**
2. **No demonstrated reachability under RL.** I show the judge *can* be fooled by
   constructed strings; I do NOT show that GRPO on the frozen Claude policy *would*
   discover these within a candidate budget. The single-token/negation strings are
   degenerate text a competent policy is unlikely to emit unprompted; the *hedge* is the
   only exploit a real policy plausibly drifts into. So the practical risk is narrower
   than "5 exploits at ~100%". A live ablation (reward vs. human-graded diagnosis over
   training) is the missing experiment — deliberately out of scope (GPU/cluster cost).
3. **Diagnosis hacking is capped at 0.30.** The 45% resolved term still requires the sim
   to actually resolve, which a hedge does not guarantee. So the *worst* a pure
   diagnosis hacker gets is 0.30, and the composed 0.55 still required a genuinely
   correct fix. The judge weakness does not by itself yield a high-reward do-nothing
   policy — an honest framing the headline must keep.
4. **`mechanism_score` makes some attacks worse, not better, for an attacker.** Several
   exploits hit `mech=1.0`, i.e. the *graded* reward also maxes out — but that's because
   the attack strips all herring tokens. A messier real model output would score lower.
   The probe uses clean adversarial strings; real exploitation would be noisier.

## What's missing / weak
- No comparison against `JUDGE_MODE="hybrid"` or `"llm"`: the hybrid judge defers to the
  LLM on borderline fraction [0.34,0.66], but every one of our exploits scores fraction
  1.0, so hybrid would NOT catch them either — worth stating, but I did not run it
  (would need network/credits; MEMORY notes Anthropic credits may be exhausted).
- Homoglyph evasion is a tokenizer artifact more than a "model strategy"; arguably it
  belongs in a separate input-sanitization finding.
- No proposed fix is implemented (brief forbids core edits). Natural mitigations:
  negation detection, a commitment/entropy penalty for naming >1 mechanism, a
  component-binding check (already partly present for cascades via shared-noun dropping),
  NFKC-normalize + ASCII-fold before stemming. These are documented, not built.

## Honest bottom line
Real, reproducible finding: the deterministic judge has structural blind spots
(negation, hedging/commitment, component binding, non-ASCII) and credits diagnoses a
human would fail. The **operationally meaningful** one is the hedge (92.9%, composes to
0.55). The **caveat that keeps this honest**: reachability under the actual RL policy is
unproven and the diagnosis term is only 30% of reward, so this is a robustness gap to
harden, not evidence of a current high-reward exploit in training.
