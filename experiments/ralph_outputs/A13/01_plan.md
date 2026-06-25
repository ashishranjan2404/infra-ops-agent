# A13 — Add multi-fault incidents (2 simultaneous faults)

## Objective
The CIDG scenario suite (`scenarios/cidg/generated/*.yaml`, ~33 specs) is 100% single-fault:
each spec has exactly one `root_cause` injected by `sim/engine.py::World.__init__`. Real incidents
frequently involve **two concurrent, independent faults** (e.g. a cert expiry that masks a
simultaneous pool leak, or a bad rollout that lands during a cache flush). An agent that latches
onto the loudest single symptom and declares victory after one fix will leave the second fault
live. This task adds **multi-fault incidents** (2 simultaneous faults) to the suite.

## Approach
1. Study the YAML schema (`sim/spec.py`) and the ground-truth engine (`sim/engine.py`).
2. Identify the constraint: the Tier-A engine injects **exactly one** `root_cause` and
   `is_resolved()` checks `root_cleared` for that single node only. The schema has no native
   second-fault field. So a *faithful* 2-fault sim needs an engine extension.
3. Honor the no-edit rule: do **not** touch `sim/engine.py`. Instead:
   - Author NEW, uniquely-named multi-fault scenario YAMLs into `scenarios/cidg/generated/`
     (numbers 80–82, confirmed unused) using a forward-compatible `secondary_faults` block.
     `sim/spec.py::_build` ignores unknown keys, so the specs still **parse and validate** today.
   - Each YAML's *primary* `root_cause` is fully engine-valid (injected & checked today).
   - Deliver a documented engine patch (`artifacts/engine_multifault.patch`) that, when applied,
     injects + requires-clearing the secondary fault — proving the design is real, not decorative.
4. Validate all new YAMLs parse + conform via `python -m sim.spec validate`.
5. Provide a self-contained test (`artifacts/test_multifault.py`) that loads each new spec,
   asserts it validates, asserts it declares exactly 2 distinct fault locations, and asserts the
   primary single-fault path still runs in the unpatched engine.

## Files to create (all task-namespaced — no shared-core edits)
- `scenarios/cidg/generated/80-multi-cert-poolleak.yaml`
- `scenarios/cidg/generated/81-multi-rollout-cacheflush.yaml`
- `scenarios/cidg/generated/82-multi-fdexhaust-cpustarve.yaml`
- `experiments/ralph_outputs/A13/artifacts/test_multifault.py`
- `experiments/ralph_outputs/A13/artifacts/engine_multifault.patch` (proposed, NOT applied)

## Dependencies
- `pyyaml` (already in requirements). `sim.spec`, `sim.engine` importable. Python 3.13.

## Risks
- **R1**: Engine only injects one fault → a 2-fault YAML is "aspirational" in unpatched sim.
  Mitigation: primary fault is real & checked; secondary is documented + delivered as a patch;
  test asserts both the parse-validity AND the patch's logic on a copied engine.
- **R2**: Unknown YAML keys silently dropped → second fault invisible.
  Mitigation: chosen on purpose for parallel safety; test makes the gap explicit, not hidden.
- **R3**: Schema validate rejects something. Mitigation: reuse only closed-vocab kinds/edges.

## Success criteria
- 3 new uniquely-named YAMLs exist, each declaring 2 distinct, independently-clearable faults.
- All 3 pass `python -m sim.spec validate` (0 errors).
- Each primary root_cause is engine-valid: `World.from_spec` runs, cascades, and the canonical
  primary fix clears the primary node.
- `test_multifault.py` passes under pytest.
- No shared core file edited.
