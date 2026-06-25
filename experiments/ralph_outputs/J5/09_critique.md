# 09 — Honest Critique

## What a reviewer will attack

1. **N=1, single stochastic sample.** This is one trace from one `gpt-5.5` call.
   It is illustrative, not evidence of a success *rate*. A re-run could pick a
   different (even wrong) iter-0 tool, or take 1 or 3 iterations. I report it as a
   mechanism walkthrough and pin the deterministic grader, but I cannot claim
   "the agent solves this class of incident" from N=1. Honest weakness.

2. **The prompt spoon-feeds upstreamness.** The cascade prompt says "it may be
   UPSTREAM ... ALL products are failing through a shared path." That is a large
   hint. The agent's iter-0 upstream diagnosis is therefore "used the hint
   correctly," not "discovered the root unaided." A harder version would strip the
   hint. This caps how impressive the diagnosis really is.

3. **Trap branch is by-construction.** "Scaling edge-proxy doesn't resolve" is true
   *because the reward function encodes saturation as a forbidden category for this
   incident*. It's a designed property demonstrated, not an emergent finding. I say
   so in the case study, but a skeptic will note the evidence is partly circular.

4. **Deterministic keyword judge.** `diagnosis_correct` is keyword-set overlap.
   The agent's sentence does contain "waf"/"regex"/"rollback"/"upstream" tokens, so
   a shallower sentence with those tokens would also pass. I mitigate by quoting the
   full sentence so a human can judge the actual reasoning.

5. **Model swap muddies "the agent."** The intended default proposer is Claude
   Haiku; credits forced `gpt-5.5`. So this case study describes the loop driven by
   gpt-5.5, not the roster default. Disclosed, but it means the trace isn't the
   "canonical" configuration.

6. **The agent's iter-0 tool was wrong** (`failover_service`). One could read this
   two ways: (a) honest evidence the trace is real and the feedback loop adds value;
   (b) the base proposer is not actually that strong and leans on the loop. Both are
   true; I lean on (a) but acknowledge (b).

## What's missing / would strengthen it
- A small N (e.g. 10 seeds × pass@k) to turn the anecdote into a rate — out of
  scope for a "case study" task but the obvious next step.
- A hint-stripped variant of the prompt to test unaided upstream diagnosis.
- An LLM-judge or human spot-check on the diagnosis sentence to de-risk the
  keyword judge.

## Net honest assessment
The deliverable is real and self-consistent: a genuine 2-iteration agent trace on a
real outage, plus a sim-verified trap counterfactual, written up with its scope and
limitations stated plainly. Its claims are narrow (mechanism, not metric) and I
believe correctly scoped. The main intellectual softness is the prompt hint and the
N=1 framing, both disclosed.
