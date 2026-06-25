# B9 — 09 Critique (honest)

## What a reviewer will attack
1. **n is tiny.** 15 episodes, only **5 distinct incidents** and 3 near-deterministic
   seeds. Every interval here — Wilson, bootstrap, cluster — is weak. A bootstrap does not
   manufacture statistical power; with 5 incident-blocks the cluster bootstrap can only
   take values in {0, 0.2, 0.4, 0.6, 0.8, 1.0}, so its "interval" is coarse and jumpy.
   This is the single biggest weakness and it is a property of the *data*, not the method.
2. **The 0/n boundary makes the bootstrap look bad.** For 3 of 5 conditions the bootstrap
   returns the degenerate `[0,0]`, which has near-zero true coverage. If someone naively
   trusted the bootstrap there they'd badly understate uncertainty. Honest conclusion:
   **Wilson remains the correct default**; the bootstrap is a *cross-check*, not a
   replacement.
3. **Seeds aren't real replication.** The 3 seeds per incident are 3/3 or 0/3 almost
   everywhere → they add little independent information. The effective sample is ~5. The
   i.i.d. bootstrap (and Wilson) both pretend n=15; only the cluster bootstrap corrects
   for this, and it's the one with the coarsest support.
4. **Cluster bootstrap model choice is arguable.** Resampling incidents answers "will REx
   generalize to a *new* incident drawn from the same population?" If instead you only care
   about these exact 5 incidents, the i.i.d. interval is the relevant one. Both are
   reported; the right one depends on the claim being made.
5. **One model only.** Data is claude-haiku-4-5 from the ablation run. Frontier data
   (`rex/runs/frontier.json`) exists for more models but uses a different scenario set and
   2 seeds/scenario; folding it in would mix designs. Left out deliberately — noted as
   future work, not silently dropped.

## What's weak / missing
- No BCa (bias-corrected accelerated) bootstrap — percentile only. At this n, BCa's
  acceleration term is itself unstable, so percentile is the defensible choice, but a
  reviewer may still ask.
- No coverage simulation to *prove* which interval has better calibration here; that would
  require a generative model of incident difficulty we don't have.

## Honest bottom line
The robustness check **succeeded and its verdict is nuanced, not a clean win**: under the
i.i.d. assumption the bootstrap corroborates Wilson (so the reported pass@1 CIs aren't
artificially tight *given* i.i.d.); but the cluster bootstrap shows the i.i.d. assumption
is optimistic — with only 5 incidents the real generalization uncertainty for REx is
`[0.0, 0.8]`, not `[0.20, 0.64]`. The actionable takeaway for the project is **add more
distinct incidents**, not change the CI estimator.

## Proposed (NOT applied) integration
A one-function addition to `compute_pass_at_k.py` could emit a `cluster_ci` column
alongside Wilson. Per the parallel-safety rule this is left as a documented proposal only;
the standalone `bootstrap_ci.py` already produces the numbers without touching core.
