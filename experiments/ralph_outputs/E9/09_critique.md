# E9 — 09 Critique (honest)

## The headline weakness: this is half a comparison
The Fireball arm is **blocked, not measured**. So strictly, E9 did not *run* the head-to-head
it set out to run — it built the harness, ran one side, and argued the other side a-priori. A
reviewer is entirely right to say "you compared 816 trajectories to a zero you assigned
yourself." The verdict is a **data-quality / seeding** verdict, defensible on coverage, spread,
and domain, but it is **not** a trained-accuracy comparison and never claims to be.

## Where a reviewer attacks
1. **`domain_match=0` for FIREBALL is asserted, not demonstrated.** It is a definitional claim
   (D&D combat vs k8s SRE). Plausible, but someone could argue *structural* transfer (the
   state→action→state shape itself) is the point, and that off-domain pretraining sometimes
   helps. We do not test that — it is exactly the experiment the blocker prevents.
2. **The synthetic positives are monocultural.** Every positive walks one canonical
   investigation→fix path. A policy seeded only on this will overfit to a single reasoning
   shape and expect clean signals — real incidents are noisy and multi-path. This is the SMR/
   PSRE point from the grill, and it is the synthetic arm's real Achilles heel. The
   perturbations (paraphrase, tool-order, jitter) vary *surface form*, not *reasoning*.
3. **`label_coverage=0.10` looks damning** until you see it is a vocabulary mismatch (15 real
   mechanisms covered; only 2 string-match the canonical set). Honest, but it means the metric
   as shipped *understates* the synthetic arm — a careless reader draws the wrong conclusion.
4. **Rewards are construction artifacts, not earned.** Positives are *built* to score 1.0; no
   model produced them. The data teaches "here is what a 1.0 trajectory looks like" — useful
   for SFT cold-start, near-useless as an RFT signal on its own (no model exploration).
5. **No live model touched the data.** We never fed these trajectories to the frozen LLM to
   confirm they read as plausible incidents to an actual policy.

## What is genuinely solid
- The augmenter is real, deterministic, offline, and self-tested; the output is well-formed and
  carries non-zero within-group spread on every one of 204 groups.
- The harness is symmetric: drop a real FIREBALL export at `--fireball-jsonl` and it scores on
  the identical vector — the blocker is *data/compute*, not *design*.
- The blocker is documented honestly and threefold (no vendored dataset, frozen-LLM project has
  no transfer stack, off-domain), not papered over.

## Net
A correct scaffold + one runnable arm + an honest blocker — exactly what the brief asks for
when the other arm needs an external dataset and a fine-tuning stack we do not have. The
verdict should be read as "for seeding, build synthetic in-domain data first; Fireball transfer
is unproven and likely off-domain," NOT as "synthetic beat Fireball 816–0."
