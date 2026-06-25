# E8 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take

**SMR:** A data-scaling study needs a learning curve score(N) on a held-out eval, swept
over log-spaced N. The deliverable should be the curve + a fitted saturating model and a
knee. Power analysis is secondary; the curve is the answer.

**PSRE:** The thing people will actually ask is "do we have enough incident coverage?"
319 trajectories across 34 families is ~9 per family. That is a coverage problem, not a
volume problem. Sweeping to 50k assumes we can *generate* more — where does it come from?

**AAAI:** Any "N needed" claim must be reproducible and must not overclaim. If you can't
run the curve, say so. I will reject a paper that shows a smooth scaling curve fit to 3
points, or one fit to synthetic data presented as real.

**RLE:** For SFT/GRPO the relevant N is trajectories *that change the policy*. Subset
sampling must be stratified or a 1k slice is all easy `bad_deploy` and the curve lies.
Also subsets should be nested so you reuse rollouts and the curve isn't seed-noise.

**DVO:** Make it a single runnable command with deterministic seeds and written manifests,
so a sweep is auditable and re-runnable. If the data isn't there, the tool should fail
loudly with the corpus size, not silently produce zeros.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**SMR → PSRE:** I disagree that this is "only" coverage. Volume and coverage are
entangled: even with all 34 families, SFT data efficiency (how many trajectories per
family before the policy saturates) IS a scaling question. The sweep answers it *per
stratum*, which is strictly more than your coverage count.

**PSRE → SMR:** And I disagree that the curve is "the answer." A curve fit to 319 real +
49,681 imaginary points is theatre. The honest answer right now is the power-analysis N
and the blocker. Don't dress up missing data as a result.

**AAAI → SMR:** With PSRE here. A knee at N=56M (which your demo fitter will happily emit
from 4 toy points) is a red flag, not a finding. The fitter must REFUSE on <4 *real*
points. If you ship the fitter, gate it hard and label any demo output as illustrative.

**RLE → DVO:** "Fail loudly" is too strong — I want the harness to *degrade*: cap N at
corpus size, still write manifests, still emit the power analysis, and set `blocked:true`.
That's more useful than aborting; the manifests prove what a real run *would* sample.

**DVO → RLE:** Fine, degrade — but then the cap must be visible in the output (actual_N vs
requested_N) so nobody misreads a capped run as a completed 50k run. Put both numbers in
every point and every manifest.

## Round 3 — synthesis

Consensus:
1. **Deliverable = harness + power-analysis N + honest blocker**, NOT a fabricated curve
   (PSRE/AAAI win over SMR's "curve is the answer").
2. **Stratified + nested subsetting** is mandatory (RLE) — preserve family×difficulty.
3. **Anti-fabrication gates** are first-class: no fit callback ⇒ no scores ⇒
   `blocked:true`; learning-curve fitter returns None on <4 real points; any demo curve is
   labelled illustrative (AAAI).
4. **Degrade-not-abort with visible cap**: actual_N vs requested_N in every output (RLE +
   DVO compromise).
5. **Power analysis uses observed reward sd (~0.22)** and reports per-arm N across a δ grid
   so the "1k/10k/50k" question gets a quantitative anchor even without the curve (SMR's
   rigor applied to what we *can* compute).
6. **Coverage is reported alongside volume**: per-family / per-difficulty counts in the
   profile, so PSRE's coverage question is answered too.
