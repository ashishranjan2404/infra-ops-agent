# D11 — Ralph Loop Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (AAAI)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes

**SMR:** Variance across seeds is THE stability question for RL. But the existing logs
are single-run. The only legitimate "now" numbers are (a) within-group reward spread —
which GRPO already uses for advantage normalization — and (b) step-to-step curve jitter.
Anything called "seed variance" must come from re-runs with controlled seeds. Don't fake it.

**PSRE:** From an ops lens, "stability" means: if I re-run the training pipeline tonight,
do I get the same model quality? That's reproducibility. We need a deterministic seed knob
first; right now the trainer has none, so the pipeline is non-reproducible by construction.
That's the headline finding, frankly — more important than a CI number.

**AAAI:** A paper claiming an RFT result without seed variance is desk-rejectable. I want
mean ± std over ≥3 seeds, ideally 5, with the CI method stated. If you can't run them,
the contribution is a *harness* + an honest negative ("not yet measured"), which is fine
IF labelled. Cross-config variance as a seed proxy is a confound and I will flag it hard.

**RLE:** Practically, GRPO with group-relative advantages can be unstable when within-group
spread collapses (all rollouts same reward → zero advantage → no signal). So within-step
std is not just noise, it's a diagnostic. I'd plot reward_std over steps and flag any
collapse. The v2 log already has `reward_std` — use it directly, don't recompute wrong.

**DOL:** Whatever script you write must run with zero external deps in this sandbox. No HUD,
no GPU, no network. Read jsonl, compute stats, emit artifacts. The GPU re-run is a separate,
clearly-marked blocked step. Don't couple the analyzer to the trainer.

## Round 2 — react to another persona by name (forced disagreement)

**RLE → AAAI:** I disagree that cross-config variance is *useless*. It's confounded, yes,
but 8b vs 30b vs 8b_v2 landing within ~0.03 mean reward of each other is real evidence the
reward signal is *config-robust*. Report it — just never call it seed variance. You're
throwing away signal by demanding purity.

**AAAI → RLE:** No. If you put "config variance ≈ 0.03" next to "seed variance" in the same
table a reader will conflate them, and reviewers assume the worst. Different n (24 vs 40),
different model — that's three confounds stacked. Put it in a clearly separate, caveated
subsection or I'd reject. We actually mostly agree on the fix (separate + labelled); we
disagree on whether it belongs in the headline. It does NOT.

**PSRE → SMR:** You're treating step-to-step curve std as a stability proxy. I push back:
that's autocorrelated within ONE seed and conflates *learning* (the curve should move) with
*instability* (noise around the trend). A rising curve has high std but is perfectly stable.
You must detrend or report last-k plateau std, not whole-curve std, or the number is
meaningless to an operator.

**SMR → PSRE:** Fair and I concede the detrend point — whole-curve std overstates instability
on a learning curve. But I disagree that reproducibility is "more important than the CI." For
an ML claim the CI on final reward IS the deliverable; reproducibility (seed knob) is the
*enabler*. Both go in. I'll add last-k plateau std AND keep the seed-knob patch as the gating
prerequisite you want.

**DOL → AAAI:** You want 5 seeds; I want you to know each GRPO seed is ~100 steps of paid
forward/backward on a rented GPU. "Just run 5" is a budget + time decision, not a script
decision. The honest deliverable is: harness ready, one command to launch, documented cost,
blocker noted. We don't disagree on rigor — we disagree on pretending the run is free.

## Round 3 — synthesis

Consensus:
1. **No real seed variance exists** and must not be fabricated — headline finding is the
   missing `--seed` knob (reproducibility gap). (PSRE, SMR, AAAI, DOL agree.)
2. Deliver a **runnable analyzer** with zero sandbox deps (DOL) that reports, from REAL logs:
   - within-step reward spread per step (use v2's logged `reward_std`; recompute for v1) (RLE),
   - **last-k plateau std** of mean_reward, not whole-curve std (PSRE), plus whole-curve for context,
   - a proper **mean ± 95% CI across seeds** code path that activates when ≥2 same-config seed logs are supplied (AAAI/SMR).
3. **Cross-config variance** included but in a separate, heavily-caveated section, never labelled seed variance (AAAI wins the headline argument; RLE keeps the data in).
4. Ship the **`--seed` patch + multi-seed driver + documented GPU/cost blocker** (DOL, AAAI).
5. Flag **within-group spread collapse** as a GRPO-specific instability diagnostic (RLE).
