# A6 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — Schema-conformance auditor
**Problems found:**
1. `secrets-vault` (file 82) is `kind: control_plane` with `discovery` edges — is `discovery`
   legal into a control_plane? Yes (`discovery` ∈ EDGE_TYPES, semantics = service→control-plane).
   But `assertions.cascades=true` requires a required/pool/queue edge; file 82's edges are
   `discovery, discovery, required` → the `ingress-gw→build-runner` required edge satisfies it. OK.
2. File 80 uses `kind: cache_flush` on a `datastore` node — kind is a root_cause vocab item, not a
   node kind; no conflict. OK.
3. Risk: did I leave any `persistent: true` without `reset_by`? No — all `persistent: false`.

## Engineer B — Realism / red-herring critic
**Problems found:**
1. Every trap is `scale_deployment`. A sharp reviewer says the traps are too uniform — a model
   could learn "never scale" and pass all 10 without understanding the mechanism. *Filter:* this
   matches the existing house set (every 40–79 file traps on scale_deployment too), so it is
   *consistent* with the corpus; diversity lives in the 8 distinct gold fixes, not the traps.
2. Honeycomb (86) and Monzo (89) are *metastable* — the honest danger is that adding capacity
   makes it worse, but the leaf schema can't encode worsen-on-scale. *Filter:* documented in
   `ordering_notes` ("adding nodes feeds the metastable churn"); accepted as a known modeling gap.
3. AWS S3 (87) root is `node_notready` but modeled as a `control_plane` node, not a `node` kind.
   *Filter:* the incident took an *index subsystem* offline, which is control-plane-like; using
   `kind: control_plane` with `node_notready` is the more faithful blast-radius. Acceptable.

## Engineer C — Pipeline-integration skeptic
**Problems found:**
1. Do these files get *picked up*? They live in `scenarios/cidg/generated/` exactly like 40–79,
   so any loader globbing that dir ingests them. But `registry.json` is NOT updated (it's a shared
   file the brief forbids editing). *Filter:* correct call — do not edit registry.json; note in 06
   that a registry entry is the only follow-up needed for harnesses that read registry metadata.
2. `meta.failure_class` — is it validated/closed? `validate()` never checks `meta.failure_class`,
   so free-form strings are fine; I set them to the root-cause kind for readability. OK.
3. Seeds 1080–1089 — any collision with existing seeds? Existing files use 1070–1072 etc.; 1080+
   is clear. OK.

## Final filtered spec
No blocking defects. Two accepted known-gaps (uniform traps; metastable worsen-semantics not
encoded) are documented, not fixed, because fixing them would require touching shared schema/files
that A6 must not modify. `registry.json` deliberately left untouched; follow-up noted.
