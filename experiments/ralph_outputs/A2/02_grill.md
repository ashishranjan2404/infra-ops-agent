# A2 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take
- **SMR:** Swapping the proposer model is fine *only if* the judge stays the deterministic
  P0 reward. If you change the model AND the judge you confound the comparison. Keep
  `score_plan(..., judge_fn=None)`. Also: a faster model with different capability changes
  the absolute pass rates — the ablation's *internal* contrasts (rex vs best_of_n etc.)
  still hold, but you cannot compare deepseek's pass@1 to glm-5p2's pass@1 as "the same run".
- **PSRE:** The whole point is the cascade/novel families. If the faster model collapses on
  cascades (gives one-action plans), `rex` has nothing to climb and the ablation looks null.
  Report per-family, not just aggregate.
- **AAAI:** 5 seeds x 30 incidents = n=150 per condition. Fine for pass@k with Wilson CIs,
  but the McNemar follow-up (run_ablation_v2) needs *aligned* (incident,seed) pairs. If a
  time-box leaves conditions with unequal completion, the pairing breaks. Either complete
  fully or document which pairs are valid.
- **RLE:** REx's diversity comes from per-node feedback, not temperature (deepseek is a
  no_temperature reasoning model). Confirm the tree actually expands >2 nodes; otherwise
  you're measuring best_of_n in disguise — the original ablation.py even warns about this.
- **DVO:** rc=143 is SIGTERM from the loop wrapper. A faster model alone won't fix it if the
  wrapper still kills at a fixed timeout. You need *graceful* time-boxing + resume, or the
  next worker inherits the same corpse.

## Round 2 — react to another persona (genuine disagreement)
- **RLE -> SMR:** I disagree that "internal contrasts still hold" is automatically safe. If
  deepseek is *too strong*, zero_shot already passes and there's a CEILING — rex shows zero
  lift not because the tree is useless but because there's no headroom. A faster *and weaker*
  model would actually be a better ablation substrate. Strength matters, not just speed.
- **SMR -> RLE:** Partly fair, but I reject "weaker is better" as a blanket rule. If it's too
  weak it floors out (everything fails, also no spread). The doctrine is *within-group reward
  spread*; pick a model with mid pass@1. We measure spread (`reward_std`) and check it's >0.
- **PSRE -> DVO:** I push back on "graceful time-box solves it." A SIGALRM that fires inside a
  `requests.post` aborts mid-episode — that episode's reward is lost AND the checkpoint may
  be stale (run_eval checkpoints every 25 eps). So "resume" can replay a few episodes. That's
  fine for *correctness* (idempotent rewards) but the wall-time accounting must not claim
  those as completed. Don't double-count.
- **AAAI -> RLE:** The node-count check is good but secondary. My blocking concern is honesty:
  if the run is partial, the paper-facing claim must say "partial, N/750", and the pass@k must
  be computed only over completed episodes — never imputed.
- **DVO -> PSRE:** Conceded — the checkpoint granularity (every 25) is the real hole. Since I
  can't edit shared `run_eval`, the wrapper must rebuild a report from whatever checkpoint
  exists and, if none exists yet, say so plainly rather than crash.

## Round 3 — synthesis
Consensus the plan must honor:
1. **Judge frozen** = deterministic P0; only the *proposer* model changes. (SMR)
2. **Report per-family + reward_std + floor_check**, not just aggregate. (PSRE, SMR)
3. **Pick a mid-strength fast model** so there's headroom for rex to lift and spread to
   measure; verify empirically, don't assume. (RLE, SMR)
4. **Graceful time-box + resume**, and **never count partial/mid-flight episodes as done**;
   if partial, label it `PARTIAL N/750` and compute pass@k only over completed. (DVO, PSRE, AAAI)
5. **Sanity-check REx node expansion** so the contrast isn't best_of_n in disguise. (RLE)
6. The smoke test already exposed a real bug (empty-checkpoint -> None report); fix the
   wrapper to degrade gracefully. (DVO)
