# E5 — Honest Critique

## The headline weakness: the deliverable's namesake is blocked
The task is "Fireball transfer." Fireball does not exist in this repo's roster or any
configured provider, so the central number — Fireball's generalization pass@1 — was not
produced. What ships is the *infrastructure* to produce it plus a baseline reference.
That is the correct response under the brief's no-fabrication rule, but a reviewer will
fairly note the experiment is **not concluded**, only **instrumented**.

## What a reviewer attacks
1. **Small sample, blended families.** n=10 with 2 seeds = 20 episodes per policy. The
   Wilson CI on glm-5p2 is wide ([0.11, 0.47]). Worse, 2 of the 10 are easy back-fill
   leaves that carry most of the passes — a single blended pass@1 flatters easy-incident
   transfer. Mitigated by the preserved per-incident map, but the top-line number is
   soft. More seeds and a pure-novel-family variant would harden it.
2. **Zero-shot only.** This measures single-shot transfer, not the REx/refinement
   transfer the larger project cares about. A reviewer wanting "does the method
   generalize" would ask for the `rex` condition on the novel set too; E5 only wired
   zero-shot to keep the scope tight and the cost low.
3. **One real baseline.** gpt-5.5 returned empty strings and Anthropic is out of
   credits, so glm-5p2 is the lone live reference. A one-baseline comparison is thin;
   the harness supports more, but only one was reachable today.
4. **Oracle is a weak model-ceiling.** It's load-bearing as a *data-validity* gate
   (proves the incidents are solvable) but says nothing about achievable model quality —
   do not read oracle==1.0 as "the task is easy."
5. **Synthetic substrate.** These incidents run on `sim/engine.py`, not a live cluster.
   "Generalization" here is to unseen *synthetic* incidents; transfer to real production
   telemetry is a stronger claim this does not make.

## What's missing
- A pure novel-family (8-incident) run and a higher-seed run to tighten the CI.
- The `rex` (refinement) condition on the novel set for a search-vs-transfer split.
- A second reachable baseline for a real cross-model comparison.
- The actual Fireball checkpoint — the one thing that turns this from scaffold to result.

## Net honest assessment
Solid, reusable, correctly-controlled harness with one real baseline and a clean
provenance trail to A8. The negative is real and stated plainly: **the Fireball transfer
result is blocked**, so E5 delivers a ready-to-fire eval and a reference number, not the
generalization verdict on Fireball itself.
