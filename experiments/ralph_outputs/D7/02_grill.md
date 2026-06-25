# D7 — 02 Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer
(REV)**, **RL Engineer (RLE)**, **DevOps Lead (DVO)**.

## Round 1 — initial take

**SMR.** Cascade-only vs mixed vs none is a clean data-mix ablation. The right
headline is the *transfer matrix*: rows = train config, cols = eval family. Just make
sure exemplars never leak into eval, and report CIs — with this benchmark size the
cells will be small.

**PSRE.** Operationally this matters: an on-call agent that only ever saw cascade
incidents may "over-diagnose" — pattern-match a simple disk-full into a multi-service
cascade and take the wrong action. The eval must catch *that specific failure*, not
just aggregate pass@1. Look at the trap-tool rate on simple incidents.

**REV.** "Training" here is in-context prompting on a frozen model. If the paper says
"trained on cascade only" and it's actually few-shot, that's a misrepresentation I'd
flag. Be explicit it's a frozen-LLM proxy or I reject.

**RLE.** The exemplar signal is the *gold fix tool* from `fix_tools`. That's a strong
oracle leak into the prompt — you're basically handing the model the answer key for a
related family. Fine as a transfer study, but say so; it's not what a reward-only RFT
would distill.

**DVO.** Whatever you build has to run in 15 minutes and re-run deterministically.
72 LLM calls is a coin flip on the cap. I want a dry-run that proves the plumbing with
zero network, and a reduced real run that proves the live path. Don't gate the
deliverable on the full sweep finishing.

## Round 2 — react to another persona by name (forced disagreement)

**RLE → SMR:** I disagree that this is a "clean" data-mix ablation. It is NOT. In a
real RFT the model distills *reward signal*; here you inject the *literal gold tool*
into the context. Those are different experiments. cascade-only-prompting helping
cascade could be pure copying of the shown tool, not learned generalization. Your
transfer matrix will look great for the wrong reason.

**SMR → RLE:** Partially fair, but you overstate it. The exemplars are from *different*
cascade incidents than the eval incidents (leakage guard), and cascade fixes are
heterogeneous (DNS, FD-exhaust, BGP, cert). So "copy the shown tool" rarely works —
the model has to map a pattern, not echo a string. I'll keep the gold-tool signal but
explicitly frame it as an *upper-bound proxy* for what training would distill.

**PSRE → REV:** You're worried about the word "training"; I'm worried you'll wave
through an eval that reports only mean pass@1. I disagree with treating the
nomenclature as the main risk. The *real* risk is an aggregate number that hides the
over-diagnosis failure mode. Mean pass@1 on simple can stay flat while the agent
quietly starts taking cascade-style actions on trivial incidents.

**REV → PSRE:** Both matter and they're not in tension. But I won't drop the
nomenclature point — a mislabeled method is a reject regardless of how good the
sub-metrics are. Add the reward_std per cell too; a flat mean with collapsing spread
is its own red flag (no trainable signal).

**DVO → SMR:** Your "report pass@2/pass@5" instinct is wasted compute here. With
2–3 seeds those estimators are meaningless. I disagree with copying the full
`eval_pass_at_k` output shape. Report pass@1 + Wilson CI + mean + std. That's it.
Keep me under the cap.

## Round 3 — synthesis

Agreements reached:
1. **Frame honestly (REV+RLE win):** this is a frozen-LLM, in-context proxy for an
   RFT data-mix ablation; the exemplar gold-tool is an *upper-bound* proxy signal.
   Document it in the config header and the spec — do not call it gradient training.
2. **Report the transfer matrix + per-cell CI, mean, and std (SMR+REV).** Drop
   pass@2/5 — under-powered (DVO).
3. **Two-tier execution (DVO):** `--dry-run` proves wiring with zero network +
   zero-leakage assertion; a reduced real run proves the live path; full sweep is
   documented as scalable.
4. **Surface the over-diagnosis failure mode (PSRE):** the deterministic judge already
   penalizes trap tools, so a drop in simple pass@1 under cascade-only *is* the
   over-diagnosis signal; call it out explicitly in verification/critique. (A dedicated
   trap-rate breakdown is logged as a future extension, not built now, to respect the
   cap.)
5. **Leakage guard is non-negotiable (SMR+RLE):** assert empty train∩eval and ship the
   assertion in the dry-run.
