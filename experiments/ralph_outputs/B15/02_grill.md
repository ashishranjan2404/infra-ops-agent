# B15 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **AAAI** (AAAI Reviewer),
**RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial take

**SMR**: The only intellectually honest comparison is single-shot vs single-shot. Our
*zero_shot* pass@1 (0.23) is the comparator to SREGym's single-attempt agents (E2E 0.40–0.61).
Leading with REx=0.90 vs SREGym=0.61 is a category error — REx is multi-attempt + oracle.

**PSRE**: SREGym runs *real* containerized faults with a mitigation oracle that checks the live
system recovered. Ours is a simulator with a hand-authored reward. These measure different
things. A 0.90 in sim does not mean 0.90 of real incidents resolved. Say so loudly.

**AAAI**: Reject-on-sight if the table implies our method "beats" SREGym SOTA. The benchmarks
share no tasks, no substrate, no models, no grader. The contribution here is a *calibrated
contextualization*, not a ranking. The caveats are the paper, not the table.

**RLE**: pass@1 is well-defined for us (binary reward >= 0.8, unbiased estimator over seeds).
SREGym's "success rate over 3 runs, 1 attempt/run" IS pass@1 — they just don't name it. Good,
the metric semantics actually line up even if everything else doesn't. Document that bridge.

**DOL**: Practically, the number an on-call lead cares about is "of real incidents, how many got
auto-resolved end-to-end." SREGym's E2E (correct diagnosis AND mitigation, oracle-verified) is
closest to that. Our reward bundles SLO-restored + root-cleared + no-collateral, which is *also*
E2E-ish. So compare our pass@1 to SREGym **E2E**, not to their mitigation-only column.

## Round 2 — react to another persona BY NAME (forced disagreement)

**PSRE → SMR**: I disagree with SMR that zero_shot is "the" comparator. SREGym agents (Stratus,
Claude Code) are themselves *scaffolded loops* — they retry, read logs, iterate within one run.
They are NOT zero-shot. The honest analogue to a scaffolded SREGym agent is our `retry_realistic`
(0.35) or `best_of_n` (0.34), not raw zero_shot. Pinning to zero_shot understates the fair line.

**SMR → PSRE**: Partly fair, but a SREGym single run has *no external oracle telling the agent it
failed and to try again* — that's the REx-no-oracle distinction. SREGym's within-run iteration is
self-directed; REx's is oracle-fed. So the fair within-our-suite analogue is **rex_no_oracle**
(0.33), which is the closest to "a capable agent looping on its own signal." I'll concede the
comparator is rex_no_oracle / best_of_n (~0.33), not zero_shot — that *raises* the honest line
but is still far below SREGym's 0.40–0.61. That gap is the real finding: SREGym tasks are harder.

**AAAI → DOL**: I challenge DOL's "compare to E2E" as too clean. Our single reward conflates
diagnosis and mitigation into one scalar; SREGym *separates* them and shows diagnosis often lags
mitigation (Claude Code: 72.6 diag vs 75.6 mit). We cannot decompose our number that way, so any
row-to-row mapping to E2E hides that we literally cannot report diagnosis-only. Put that in caveats.

**RLE → SMR**: Disagree that the metric semantics "line up." Our pass@1 averages a *graded*
reward thresholded at 0.8; theirs is a *binary oracle* per axis. Thresholding a continuous reward
introduces a knob (0.8) that has no SREGym counterpart — slide it and our pass@1 moves. That's not
the same estimator. Must disclose the threshold sensitivity.

**DOL → PSRE**: I'll push back — for an on-call lead, "with noise" is the realistic SREGym column
(observability is always noisy in prod), and SREGym's E2E *drops* under noise (60.7→53.7 for
Claude Code). Our sim has `monitoring_degrades`/noise knobs mostly off. So even the honest line
should compare to SREGym's *no-noise* numbers and note our sim is closer to no-noise.

## Round 3 — synthesis

Consensus:
1. **Headline must not be a ranking.** Frame as contextualization with non-equivalence front-and-center.
2. **Report a band of our comparators**, not one: zero_shot (0.23) / best_of_n (0.34) /
   rex_no_oracle (0.33) as the "single-run-ish" band, and rex (0.90) explicitly flagged as
   *multi-attempt + oracle*, which has NO SREGym counterpart (SREGym is 1 attempt/run).
3. **Compare to SREGym E2E (no-noise)** as the primary cross-axis row, since both bundle
   diagnose+mitigate, while noting we cannot decompose diagnosis vs mitigation (AAAI/RLE point).
4. **Family↔partition mapping** (simple↔Ported, cascade↔Similar, novel↔New) is a *loose analogy*,
   defensible mainly for novel↔New (both = unseen failure modes); label it explicitly.
5. **Disclose the 0.8 threshold knob** and the noise-off assumption.
6. The genuine, defensible finding: **SREGym's live single-attempt tasks are materially harder
   than our simulator's single-run conditions; our REx lift is real but is a different regime
   (multi-attempt + oracle) and must not be read as beating SREGym.**
