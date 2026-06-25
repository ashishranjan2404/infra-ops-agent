# A13 — Ouroboros (self-critique as 3 engineers in sequence)

## Engineer 1 — "the validator pedant"
**Problems found:**
- P1.1: `assertions.buried_gun_exists=true` requires `observation.smoking_guns` non-empty AND every
  gun's `node` must be in topology (spec.py:341-343). If I add 2 guns and fumble a node name, the
  spec FAILS validate. → Must use exact node names.
- P1.2: `assertions.cascades=true` requires ≥1 required/pool/queue edge (spec.py:346-349). A 2-fault
  spec where the two faults are on isolated nodes with only `optional` edges would FAIL. → Every
  spec must have a `required` edge in the blast path.
- P1.3: SLO with `node` not in topology fails (spec.py:329). Both SLO victims must be real nodes.
- P1.4: pool edges require `resources.pool_size` on the target (spec.py:306-309). Avoid pool edges
  unless I set pool_size. → Use `required` edges only to stay simple/valid.

**Filtered:** all four are hard validate constraints. Adopt: required edges in blast path, exact
node names everywhere, both SLO victims real, two guns with correct nodes, no pool edges.

## Engineer 2 — "the construct-validity skeptic"
**Problems found:**
- P2.1: If the secondary fault's `slo_node` equals the PRIMARY victim, then fixing the primary alone
  could already drag that SLO green and the second fault is invisible to `is_resolved` even after
  the patch. → Secondary fault MUST have its OWN distinct SLO victim node, downstream of the
  secondary fault only (not reachable from the primary fault). Enforce in topology.
- P2.2: For the masking spec (81), if both faults feed the SAME victim, the agent can't tell them
  apart and "masking" is just noise. Masking means: fault A's symptom dominates the shared signal;
  only after A is fixed does B's signature surface. The smoking gun for B should be `buried_under`
  a large number to model that it's hidden until A clears. → set B's gun buried_under high.
- P2.3: The secondary `fix_tool` must be in `REMEDIATION[kind]` or even after the patch the fix
  never clears it (apply_action checks tool ∈ REMEDIATION[kind] AND target==fault_node). → Cross-
  check every fix_tool against the REMEDIATION dict in engine.py.

**Filtered:** P2.1 and P2.3 are correctness-critical → adopt (distinct downstream victim per fault;
fix_tool ∈ REMEDIATION). P2.2 adopt for spec 81 (high buried_under on secondary gun).

## Engineer 3 — "the over/under-engineering auditor"
**Problems found:**
- P3.1: Over-engineering risk — inventing a rich `secondary_faults` schema with rate_law,
  persistent, reset_by per secondary. The first cut doesn't need latent counters; keep secondary to
  {location, kind, severity, fix_tool, slo_node}. YAGNI. → Keep minimal.
- P3.2: Under-engineering risk — if I DON'T deliver the engine patch, the whole task is decorative
  and a reviewer dismisses it. The patch is the load-bearing artifact proving the design is real. →
  Patch is mandatory, must be syntactically a real unified diff against current engine.py/spec.py.
- P3.3: The test `test_primary_runs_unpatched` must not depend on the patch (we don't apply it).
  Verify it imports the *current* engine and only exercises the primary path. → keep test patch-free.
- P3.4: Don't edit `registry.json` (shared file, and brief forbids editing shared state). The new
  specs simply won't have registry entries; that's acceptable for added data and avoids a merge
  conflict with parallel workers. → leave registry untouched, note it.

**Filtered:** all adopted. Minimal secondary schema; ship a real patch; patch-free test; no registry edit.

## Final filtered spec deltas
1. Every spec: ≥1 `required` edge; two distinct SLO victims, each downstream of only its own fault.
2. Secondary `fix_tool ∈ REMEDIATION[kind]`; primary likewise (already true).
3. Two smoking_guns per spec (one per fault); secondary gun `buried_under` high on masking spec 81.
4. Secondary block minimal: location, kind, severity, fix_tool, slo_node.
5. Ship a real unified-diff `engine_multifault.patch`; tests are patch-free; registry untouched.
