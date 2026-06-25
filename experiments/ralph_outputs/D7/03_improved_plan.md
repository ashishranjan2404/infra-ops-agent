# D7 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Honest framing baked into artifacts (accepted: REV, RLE).** The config header and
   spec now state explicitly: frozen-LLM, in-context proxy for an RFT data-mix
   ablation; the exemplar gold-tool is an *upper-bound* proxy for distilled signal —
   not gradient training. This is the single biggest correctness fix.
2. **Output shape trimmed (accepted: DVO).** Dropped pass@2/pass@5 (meaningless at
   2–3 seeds). Per cell we report: `pass@1`, Wilson `ci95`, `mean_reward`,
   `reward_std`, and the `eval_incidents` used.
3. **`reward_std` per cell added (accepted: REV).** A flat mean with collapsing spread
   = no trainable signal; surfacing std catches that.
4. **Over-diagnosis named as the headline operational risk (accepted: PSRE).** A drop
   in simple pass@1 under cascade-only training IS the over-diagnosis signal because
   the deterministic judge already penalizes trap tools (`scale_deployment` on a
   disk-full, etc.). Documented in verification + critique.
5. **Two-tier execution (accepted: DVO).** `--dry-run` (zero network) proves split +
   leakage + scoring wiring; a reduced "smoke" real run proves the live LLM path; the
   full sweep is parameterized and documented as scalable when compute allows.
6. **Leakage assertion shipped (accepted: SMR, RLE).** `build_split` removes train
   names from every eval family; the dry-run output is checked for empty intersection.

## Critiques REJECTED and why
- **RLE: "remove the gold-tool exemplar, it's an oracle leak."** Rejected. Removing it
  leaves nothing to inject — the experiment becomes "frozen prior vs frozen prior."
  The gold tool is the closest in-context proxy for what an RFT distills; cascade fixes
  are heterogeneous (DNS/FD/BGP/cert) and exemplars come from *different* incidents
  than eval (leakage guard), so naive string-copy rarely passes. We instead **label it
  an upper-bound proxy** and keep it. (Compromise SMR proposed in R2.)
- **SMR: "report the full pass@k matrix shape from eval_pass_at_k."** Rejected per DVO:
  under-powered at this budget. pass@1 + CI only.
- **PSRE: "build a dedicated trap-rate-on-simple breakdown now."** Deferred, not
  built — it would add scenarios/time against the 15-min cap, and the judge's trap
  penalty already makes a simple-pass@1 drop interpretable as over-diagnosis. Logged
  as a future extension in 09.

## Final method (unchanged core)
Three configs {cascade, mixed, none} × two eval families {simple, cascade}, frozen
proposer, deterministic judge, Wilson CI. Headline = transfer deltas
H1 = p1(cascade|cascade) − p1(cascade|none) and
H2 = p1(simple|cascade) − p1(simple|mixed).
