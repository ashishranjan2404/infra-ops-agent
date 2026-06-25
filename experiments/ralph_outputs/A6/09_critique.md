# A6 — 09 Critique (honest)

## What a reviewer will attack
1. **Uniform traps.** Every scenario's `trap_actions` is `scale_deployment` on a downstream
   victim. A model could exploit a degenerate "never scale" heuristic and pass all 10 without
   any causal understanding. This mirrors the existing 40–79 corpus (so it's *consistent*, not
   *novel*), but it caps the discriminative value of these particular scenarios.
2. **Metastable cases under-modeled.** Roblox, Honeycomb, and Monzo are genuinely *metastable*:
   the real danger is that adding capacity makes the collapse worse (positive feedback). The leaf
   schema used here cannot encode worsen-on-scale (that needs `root_cause.rate_law.worsened_by`
   and `persistent: true`). I documented this in `ordering_notes` but did NOT encode it, so the
   sim will treat these as ordinary cascades. This is the biggest fidelity gap.
3. **Lossy fix-tool mappings.** GitLab DB deletion → `clear_cache` (really a backup restore) and
   AWS S3 typo → `restart_service` (really an index-subsystem rebuild) are abstractions forced by
   the closed 25-tool action space. Defensible and documented, but a domain expert may object.
4. **No source URLs / `urls: []`.** Provenance is only in the `source` string. Fine for the sim,
   weak for an AAAI artifact.
5. **registry.json not updated.** Harnesses that read registry-level `gold_root`/`red_herrings`/
   `family` metadata won't see these 10 until 10 entries are added. I deliberately did not touch
   the shared file (parallel-safety rule), so this is an intentional, documented follow-up.
6. **No end-to-end run.** I validated structure but did not execute `sim/engine.py::propagate()`
   on these specs to confirm the cascade/loudest-alert emergent properties actually hold at run
   time (the validator only does static pre-checks). That dynamic check is the missing proof.

## What's genuinely solid
- 10/10 parse + validate, 0 errors; 8 distinct root-cause kinds; no id collisions; zero edits to
  shared code/data. The deliverable is real, schema-correct, and self-contained.

## Honest status
Completed as a data-authoring task: real, validated artifacts. NOT blocked. The unaddressed items
(worsen-semantics, registry entries, dynamic engine run, source URLs) are scoped-out follow-ups,
not failures of the core deliverable.
