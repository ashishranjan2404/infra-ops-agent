# B4 — Honest Critique

## What a reviewer attacks

1. **Single-label collapses the novel∩cascade overlap.** facebook_bgp_backbone, cloudflare_*
   and several real outages are *both* cascading *and* novel. My primary-type rule files them as
   novel (provenance wins). That is a defensible convention, but the "cascade" stratum is then
   biased toward *synthetic* cascades, and the "novel" stratum carries most of the hard cascades.
   A reviewer could argue the novel REx lift is partly a cascade-difficulty lift. Mitigation
   would be a 2-axis label (novelty × cascade) — out of B4 scope, flagged as follow-up.

2. **Most of the corpus is unevaluated.** 19/51 incidents (incl. ALL 10 unregistered novel
   real-outages and the 6 a11 cascades) have no pass@k results because they're not in
   `registry.json`, so the harness never ran them. The novel table's evaluated set is therefore
   the 10 *registry* novel incidents, not the 20 I classified. The tables disclose this honestly,
   but the headline "REx wins on novel" rests on 10 incidents × 5 seeds, not 20.

3. **REx cells are saturated (reward_std = 0, pass@1 = 1.0) on every type.** This is real in the
   source runs but is a trainability red flag (HUD doctrine: zero within-group spread = no
   gradient signal). It suggests the REx oracle makes these incidents trivially solvable — the
   *interesting* spread lives in zero_shot/best_of_n/rex_no_oracle. B4 surfaces it but doesn't
   fix it (not its job).

4. **Wilson CIs are wide on the per-type split.** novel n=30 (glm) / n=50 (deepseek) per
   condition gives e.g. 0.167 [0.073,0.336] — the simple-vs-novel zero_shot gap is real but the
   per-cell CIs overlap across some conditions. No formal between-type significance test is
   provided (deferred in 03, REV's request).

5. **Classifier fallback is heuristic for 9 incidents** (3 mechanics + the multi_* files via
   mechanics). `assertions.cascades` + SLO-node-count is a reasonable proxy but not ground truth;
   a mislabel there would silently misfile an incident. T3/T4 only validate the 32 registry-backed
   labels; the 19 fallbacks are validated by construction (name-rule/real-outage) or proxy
   (mechanics), not against an external gold label.

## What's genuinely solid
- Parity is exact (T8, 105/105) — the tables cannot drift from A1/A2.
- Zero classifier-vs-result mismatches — my labels agree with both published runs on every
  incident they share.
- Full 51/51 coverage with explicit disclosure of the unevaluated tail.
- No shared-core edits; fully re-runnable; stdlib + pyyaml only.

## Net
The deliverable (classifier + 3 stratified tables from real numbers) is complete and correct for
the data that exists. The honest limitation is data coverage (19 unrun incidents) and the
saturated-REx / single-label-axis caveats — all disclosed, none fabricated.
