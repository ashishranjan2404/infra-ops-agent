# F4 — 02_grill (Ralph Loop: 5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial take

**SMR.** Figures must show uncertainty. pass@1 bars without CIs are uninterpretable at
n≈126. Use Wilson intervals (already in the JSON), not normal approximation — pass@1 near
1.0 would otherwise produce CIs that exceed 1. Add a pass@k scaling curve; a single k=1 bar
hides that REx hits ceiling by k=2 while baselines need k=5.

**PSRE.** The story SREs care about is *cascade and novel* incidents — that's where on-call
burns. Don't bury the family breakdown. An overall 0.90 vs 0.23 bar is nice but the honest,
load-bearing claim is "REx holds on cascade/novel where zero-shot collapses to 0.07/0.17".

**REV.** Two different models (glm-5p2 in A1, deepseek-v4-pro in A2) on different figures is a
red flag unless labeled. I will assume p-hacking if the headline bar chart and the
significance test silently use different models. Label the model on every figure.

**RLE.** The `rex_no_oracle ≈ best_of_n` result is the most important honest finding (A2's
own one-liner says the lift is the oracle feedback, not the tree). The figures must make that
visible, not airbrush it. If REx(no-oracle) sits with the baselines, show it sitting there.

**DVO.** Make it reproducible: one script, headless backend, deterministic inputs, no network,
logged output. If a reviewer can't run `python3 make_figures.py` and get byte-similar PNGs,
it's not an artifact, it's a screenshot.

## Round 2 — react to another persona (genuine disagreement)

**REV → SMR.** Disagree on scope. You want *more* figures (curve + CIs + families). I want
*fewer, denser* figures. Six figures for a 5-condition ablation is padding; an AAAI reviewer
reads a 6-panel dump as "no single figure makes the case." Collapse to ~3 core figures.

**SMR → REV.** Rejecting that. These are *artifacts in a results dir*, not the 1-figure budget
of a camera-ready. Over-supplying figures so the writer can pick is correct here. But I concede
each figure must stand alone, so I'll enforce per-figure model labels and self-contained captions
— which also answers your R1 point.

**PSRE → RLE.** Push back on framing `rex_no_oracle ≈ best_of_n` as the headline. Operationally
nobody deploys "REx without the oracle." The deployable artifact is full REx + the *learned*
harness (harness_synth_v2). The figure set must include the harness generalization, otherwise
we've shown a method that needs a hand-written oracle — which is exactly the strawman a reviewer
kills. RLE's point is true but it's a caveat, not the thesis.

**RLE → PSRE.** Partly concede: yes, include the harness figure (fig6). But I will not let the
oracle caveat be hidden. Keeping REx(no-oracle) as a labeled bar *next to* the harness figure is
the honest pairing: "here's the ceiling with a perfect oracle, here's what a learned harness
recovers." Both must ship.

**DVO → REV.** Disagree with "fewer figures = cleaner." Fewer, denser figures means I have to
re-edit the script every time the writer wants a different cut. Six small, single-responsibility
figures are *more* maintainable and each regenerates independently. Maintainability beats density
for an artifact directory.

## Round 3 — synthesis

Consensus reached:
1. **Six figures, each self-contained and model-labeled** (SMR + DVO win on count; REV's
   stand-alone requirement adopted via labels + caption text baked into each axes).
2. **Wilson CIs everywhere**, never normal approx (SMR).
3. **Family breakdown is first-class** (fig2), because cascade/novel is the SRE thesis (PSRE).
4. **pass@k scaling curve** (fig3) to show REx reaches ceiling early (SMR).
5. **Keep REx(no-oracle) visible** as its own bar in figs 1–3 — do not airbrush the honest
   "oracle does the work" finding (RLE), AND ship the learned-harness generalization fig6 so the
   deployable story is also told (PSRE).
6. **McNemar as a paired discordant-pair figure** (fig4) using A2, with model + n labeled (REV).
7. **One runnable, headless, network-free script** with a captured log (DVO).
