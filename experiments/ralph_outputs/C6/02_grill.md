# C6 — 02 Grill (5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take

**SMR:** The right experiment. The proposer is a mutation operator inside a fixed
search; the cleanest ablation is to vary ONLY that operator and hold the search,
splits, labels, evaluator, and seed constant. The dependent variables that matter are
held-out accuracy and held-out false-allow count, not train score (train score is
trivially maximizable / can overfit the 7 train incidents).

**PSRE:** I care about ONE number: held-out false-allows. A false-allow means the
synthesized harness let a *dangerous* action through (e.g. draining the last Ready
node). I do not care if model A gets 0.80 train and model B gets 0.78 if A produces a
rule-set that false-allows on held-out and B doesn't. Report the held-out FA per model
prominently.

**AAAI:** n=3 incidents held-out, n=7 train, one seed. That is not a benchmark, it is
an anecdote. Any "proposer X > proposer Y" claim needs multiple seeds and CIs or it is
noise. Also: the hand-written baseline is the same for all proposers — make sure it's
in the table as the reference line.

**RLE:** The search is Thompson sampling with budget 8. With such a tiny budget the
result is sensitive to which node gets expanded, which depends on the seed AND on the
stochastic proposer outputs. Fixing seed=0 fixes the bandit RNG but NOT the LLM
sampling — gateway reasoning models ignore temperature. So runs aren't bit-reproducible.

**DOL:** Operational reality: the default proposer (claude-haiku) is dead — Anthropic
credits exhausted. So this whole task is *forced* to be a cross-provider study. That's
fine, but be explicit that we are NOT comparing against the intended haiku proposer;
we're comparing the reachable substitutes.

## Round 2 — react to another persona (genuine disagreement)

**AAAI → SMR:** You say held-out accuracy is the DV. I disagree it's sufficient. With
only 3 held-out incidents, accuracy moves in coarse jumps; a single label flip swings
it. Report the *confusion counts* (FA, FB) not just accuracy — those are interpretable
even at n=3, whereas a 0.64 vs 0.71 accuracy delta is within noise.

**RLE → AAAI:** You keep demanding multiple seeds and CIs. Under a 15-minute compute
cap with reasoning proposers taking ~100s per 8-node run, 5 seeds × 3 models = 15 runs
≈ 25+ min — over budget. I reject "must have CIs" here. The honest framing is a
**case study with documented non-determinism**, and we SAY the result is suggestive,
not significant. Demanding CIs you can't afford just produces fabricated rigor.

**PSRE → SMR:** You imply train overfit is the main risk. I disagree about emphasis.
The dangerous failure isn't overfit-to-train, it's a proposer that writes an
*over-broad* block rule (e.g. `restart_pod` always blocks) that scores fine on the
weighted reward because false-allows are punished 2x — it trades false-allows for
false-blocks. A harness that blocks the correct fix is an outage too. So I want
held-out **false-BLOCK** in the table next to false-allow, with equal billing.

**DOL → AAAI:** You called n=3 an anecdote. Operationally I don't need a benchmark, I
need to know "if my proposer LLM changes (vendor swap, credit outage), does my
synthesized harness silently get worse?" That is a real ops question and even a 3-model
case study answers it directionally. Don't let perfect-benchmark be the enemy of a
useful signal.

**SMR → RLE:** Agreed the runs aren't bit-reproducible, but I push back on treating
that as a flaw to hide. It's a *finding*: if held-out FA is stable across proposers
DESPITE LLM-sampling noise, the harness interpreter + evaluator are doing the heavy
lifting and the proposer matters little. If FA swings wildly, the proposer matters a
lot. Either way the non-determinism is informative, not just a caveat.

## Round 3 — synthesis

Consensus reached:
1. **Primary DV = held-out confusion counts** (false-allow AND false-block), with
   accuracy secondary. (AAAI + PSRE win over accuracy-only.)
2. **Frame as a case study**, not a benchmark: single seed, 3 reachable proposers,
   under a hard compute cap; explicitly note non-determinism and that the *intended*
   haiku proposer is unreachable (Anthropic credits). (RLE + DOL.)
3. **Always show the hand-written baseline** as the reference row — it's the same for
   all proposers and is the thing we're trying to match/beat. (AAAI.)
4. The interesting scientific question is variance attribution: is held-out safety
   driven by the proposer or by the fixed interpreter/evaluator? Report whether FA is
   stable across proposers. (SMR.)
5. Train score is reported but de-emphasized as a possibly-overfit quantity. (SMR.)
