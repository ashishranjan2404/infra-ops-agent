# B14 — The Grill (5 personas, 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial takes
- **SMR:** A cost-normalized metric is the right move. pass@1 alone hides that REx fires N=4
  proposer calls per job. pass@1-per-dollar is the efficiency frontier point. But cost must be
  *real* or *clearly modelled* — don't dress up an assumption as a measurement.
- **PSRE:** In an actual incident the dollar isn't the binding constraint — MTTR is. A metric
  that optimizes $/pass could pick a cheap-but-wrong policy. Cost-efficiency is a *secondary*
  axis, not the objective. Fine as a reviewer-facing number, dangerous as a training signal.
- **AAAI:** If tokens aren't logged, this is an estimate, and estimates invite "garbage in".
  I'll attack any unstated assumption. Show the call-shape derivation from the actual code,
  and separate real prices from invented ones.
- **RLE:** The call counts are knowable exactly from `eval_pass_at_k.py` (zero_shot=1, best_of_n
  =4, rex=budget=4). The judge is the deterministic P0 scorer — no LLM call — so judge cost is
  $0. That's the load-bearing simplification; get it right and the model is defensible.
- **DVO:** Make it a script that runs on the result JSONs already on disk, no API calls, no
  cluster. Reproducible in <1s. And surface $/100-incidents — that's the number ops budgets in.

## Round 2 — genuine disagreement (react by name)
- **PSRE → SMR:** You call pass@1-per-dollar "the right move". I disagree. A frontier model at
  $5/$25 that one-shots an incident can have *worse* $/pass than a cheap model run 4x, yet be
  the only thing that actually resolves a SEV1. Cost-efficiency rankings can be actively
  misleading for high-severity work. Report it, but don't crown a "winner" by it.
- **SMR → PSRE:** Partly fair, but you're moving the goalposts. The metric answers "accuracy per
  dollar", and it answers it honestly. Nobody said it's the *only* objective. Your MTTR point is
  a *different metric* (that's task A9), not a flaw in this one. I reject the framing that a
  correct secondary metric is "dangerous".
- **AAAI → RLE:** You assert judge cost is $0 "because deterministic". Prove it. `scoring.py`
  *does* contain an LLM judge path with max_tokens=8. If any run used it, your $0 is wrong.
- **RLE → AAAI:** Checked: the pass@k harness scores via `score_plan` → the P0 deterministic
  judge (runs the simulator). The LLM-judge path exists but is not on the eval hot path. So $0
  is correct *for the modelled path* — and I expose `JUDGE_CALLS=0` as an overridable constant
  so if someone wires the LLM judge, they flip one number. I concede it must be explicit, not
  silent. Done.
- **DVO → SMR:** Your "60% output utilization" is a guess. If a reviewer assumes 100% (max_tokens
  fully used), REx's absolute $ doubles. SMR: agreed it's a guess — that's why it's a single
  parameter (`OUTPUT_UTIL`/`output_token_utilization`) and I report it in the table header. The
  *ranking* is invariant to it (it scales all conditions of a model by the same factor), so the
  pass@1-per-$ comparison across conditions of one model is robust; only cross-model absolute $
  shifts. That's the honest caveat.

## Round 3 — synthesis
Consensus reached:
1. Ship pass@1-per-dollar as a **secondary, reviewer-facing** efficiency metric — never as a
   training objective (PSRE's caveat goes in the critique).
2. **Real vs assumed prices must be flagged per row** (`price_assumed`). Claude prices real;
   gateway/fireworks slugs assumed. (AAAI)
3. Call-shape derived from code, **judge = deterministic = $0**, exposed as an overridable
   constant. (RLE/AAAI)
4. Every assumption (output utilization, input tokens, retry expected-calls, model prices) is a
   named, overridable constant; the table header states the basis. (DVO)
5. Report `$/100-incidents` and `cost x vs zero_shot` alongside the ratio — those are what ops
   and reviewers actually read. (DVO/SMR)
