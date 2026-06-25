# B10 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SR** Senior ML Researcher · **SRE** Principal SRE · **REV** AAAI Reviewer ·
**RL** RL Engineer · **DO** DevOps Lead.

## Round 1 — initial take

**SR:** A learning curve over GRPO steps is fine, but call it what it is: pass@1 is being
*derived* from a continuous reward by thresholding. That's a legitimate metric only if you
state the threshold and show it's the same one used elsewhere. Otherwise it's an arbitrary knob.

**SRE:** The 0.8 threshold maps to "incident resolved" (SLO restored + root cleared + no trap).
That's the operationally meaningful bar. If the model never clears 0.8, then operationally it
resolved zero incidents — that's the honest story, however unflattering.

**REV:** With n=24 rollouts per step, a single pass@1 point has a huge CI. Plotting bare points
without confidence bands is misleading. And steps are autocorrelated (same policy lineage), so
don't oversell any "trend."

**RL:** The `rewards` array at a step is a GRPO *group batch* spanning multiple scenarios. pass@1
here is a batch-level pass rate, not per-task. Fine for a curve, but don't claim per-incident pass@1.

**DO:** Make it a CLI that auto-discovers `runs/*.jsonl` and degrades gracefully on a missing/empty
log. The thing has to run on whatever logs are actually on disk, not a hardcoded path.

## Round 2 — react to another persona (genuine disagreement)

**RL → SRE:** I disagree that we should *only* show τ=0.8. If pass@1 is flat-zero, the curve is a
flat line at the x-axis and teaches the reader nothing about whether training moved the policy.
Reward clearly moves within [0.4, 0.78]. A flat-zero plot hides real learning dynamics.

**SRE → RL:** Hard disagree on *replacing* 0.8. Move the bar to make the curve look alive and you've
reward-hacked your own figure. 0.65 is not "resolved" — it's a partially-correct diagnosis. If you
show 0.65, you must label it as that and keep 0.8 as the headline.

**REV → SR:** Pushing back on "just state the threshold." Stating it isn't enough — you have to show
the reward *ceiling*. If max reward is 0.78, a 0.8 pass bar is unachievable by construction, and a
reader who only sees pass@1≈0 will wrongly conclude the model learned nothing. Report the reward
range so the zero is interpretable.

**DO → REV:** Confidence bands are nice but secondary to *the script not crashing on a 14-line log
with a truncated last line*. I want robustness tests before I want Wilson intervals.

**SR → DO:** Disagree on priority — robustness without a correct metric is a fast path to a
confidently-wrong figure. The pass@1 derivation is the load-bearing part; test that first, then
harden I/O.

## Round 3 — synthesis

Consensus reached:
1. **Headline = τ=0.8** (operational "resolved", reused from `rex/eval_pass_at_k.py`). Keep it even
   though it's flat-zero — that's the honest result, and we report the reward range so the zero is
   interpretable (REV + SRE win).
2. **Companion = τ=0.65** explicitly labeled "substantially-correct diagnosis", to expose real
   per-step movement (RL's point, but boxed by SRE's anti-hacking guardrail).
3. **Wilson 95% CI bands** on every pass@1 line (REV); plot `mean_reward` as a faint reference so
   the reader sees the underlying continuous signal (SR).
4. **CLI auto-discovers `runs/*.jsonl`, robust to blank/malformed/empty-reward lines** (DO), with
   self-tests covering BOTH the metric and the I/O (SR + DO).
5. Label the metric a **batch-level pass@1 over GRPO rollouts**, not per-incident (RL).
