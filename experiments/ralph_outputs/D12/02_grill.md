# D12 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take
- **SMR:** Group size in GRPO is the number of samples for the within-group baseline. Going
  4→8 cuts the baseline-mean standard error by 1/√2 (≈29%) and halves its variance. That's the
  whole statistical story; advantage = r − mean_g(r). It helps *gradient quality*, not reward ceiling.
- **PSRE:** Care more about whether the trained policy actually diagnoses incidents better. A
  cleaner gradient that converges to the same flat reward helps no on-call engineer. Show me the
  reward curve, not the SEM.
- **AAAI:** Any "does X help?" claim needs a controlled A/B with matched compute and a seed
  sweep. group=8 doubles rollouts/step — if you compare against group=4 at equal *steps*, you've
  confounded group size with total samples. Reviewers reject that instantly.
- **RLE:** The param is `--group`; it's threaded to Job.start, ts.run, and trainer.step(group_size=).
  Note the v2 default is 6, but the logged baseline ran at 4. Use the **logged 4** as the real baseline.
- **DVO:** group=8 = 80 rollouts/step vs 40. That's 2× wall-clock and 2× cost per step. Under a
  15-min cap you will NOT finish 30 steps. Decide that up front.

## Round 2 — react to another persona BY NAME (genuine disagreement)
- **SMR → AAAI:** I disagree that matched-compute is the only fair frame. The *question asked* is
  "does more rollouts help?", which is explicitly a per-step group-size question. Holding steps
  fixed and paying 2× is a legitimate framing — you're asking if spending more per step pays off.
  Matched-compute is a *different* question (group8@15steps vs group4@30steps).
- **AAAI → SMR:** Then you must report BOTH, or you'll over-claim. If group=8 wins at fixed steps
  purely because it saw 2× data, that's not a group-size effect, it's a sample-count effect. State
  which you're measuring. I hold my objection.
- **PSRE → SMR:** Your SEM math is fine but you're answering the wrong question. The baseline run
  went 0.522→0.491 — *flat*. The v2 author already diagnosed the cause: too few tasks + a coarse
  reward term maxed early. Shrinking baseline-mean noise does NOT add learnable headroom. So 4→8
  is, at best, a second-order fix. I think it mostly burns compute.
- **RLE → PSRE:** Partly agree, but you overstate it. A noisier baseline injects gradient variance
  even when headroom exists — it can stall learning that *would* otherwise happen on the better
  v2 grader. So 4→8 is a real, if modest, win. It's just not THE fix.
- **DVO → AAAI:** Your seed-sweep demand is unaffordable here. One forked slug, 15-min cap. I'd
  ship the config + a single smoke + the projection, and label it a projection, not a result.

## Round 3 — synthesis
Consensus: (1) The param is `--group`, baseline = the **logged group 4**, not the v2 default 6.
(2) 4→8 gives a *mathematically exact* baseline-mean error reduction of 1−1/√2 = 29.3% (variance
−50%) — derive sigma from the real log, don't assert it. (3) This is a **second-order** improvement:
it does NOT address the diagnosed flat-reward root cause (few tasks / low headroom), so honesty
requires saying "more rollouts help the *gradient*, not necessarily the *reward ceiling*." (4) The
A/B has two valid framings (fixed-steps vs matched-compute) — document both; don't conflate.
(5) Under the 15-min cap a full run is infeasible → deliver config + smoke path + projection +
documented blocker. PSRE's "don't oversell" and AAAI's "two framings" both make it into the spec.
