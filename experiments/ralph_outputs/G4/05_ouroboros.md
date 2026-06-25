# 05 — Ouroboros (3 sequential self-critiques of the spec)

## Engineer 1 — "the parser is fragile"
Problem: `load_why_table` parses a Python dict *literal* out of `scoring.py` with `ast`. But
the `why` dict is written inline as `{ ... }.get(a.get("tool"), default)` — it is the
**receiver of a `.get()` call**, not a bare assignment. A naive `ast.literal_eval` of a line
won't find it. I must walk the AST for a `Dict` node whose keys include `"scale_deployment"`,
or fall back gracefully (why is non-essential enrichment). **Fix:** AST-walk all `Dict`
nodes, pick the one keyed by the known trap tools; if none, return `{}` and set `why_label`
to null rather than crashing. Test 5 becomes "if a why-table is found it contains
scale_deployment," tolerating absence.

## Engineer 2 — "fault_node extraction and target matching are under-specified"
Problem: the spec says `fault_node = root_cause.location head`, but some YAMLs use
`a -> b` location strings (cascades). And the taxonomy claims a trap is "mechanism-
conditional," yet many YAML traps carry an explicit `target` equal to the fault_node, while
the *gold fix* also targets the fault_node — so the contrast "trap on X vs fix on X" is
about the *tool*, not the target. The report must not imply traps are wrong because of
*where* they point; they are wrong because the *tool* is causally inert for that
failure_class. **Fix:** record both `trap.target` and `fault_node`; in the report frame the
contrast as tool-level (scale vs increase_memory_limit on the SAME node). Also handle the
`->` split defensively.

## Engineer 3 — "over-claiming and untested edges"
Problems: (a) Test 2 hard-codes `n_with_trap >= 40` — if the YAML set shrinks the test
falsely fails; better: `n_with_trap == n_scenarios` OR `>= 0.9·n_scenarios` (we measured
51/51, but keep a margin). (b) The report risks claiming SREGym "has nothing" — I only read
the paper HTML + abstracts, not the full source tree; I must say "as described in the
published oracle design (arXiv 2605.07161) and the benchmark's documented evaluation," and
flag that a code-level audit of the SREGym repo was not performed. (c) No test that the JSON
is actually written to disk. **Fix:** relax Test 2 to a ratio, soften the report claim with
an explicit evidence-scope caveat, add a test that `main()` writes a parseable file.

## Final filtered spec (deltas applied)
- `load_why_table`: AST-walk `Dict` nodes; tolerate absence → `{}`.
- Records carry `trap.target` AND `fault_node`; report frames contrast at TOOL level.
- Defensive `location.split("->")[0]`.
- Test 2: `n_with_trap >= 0.9 * n_scenarios`; add Test 6: `main()` writes valid JSON file.
- Report: explicit "evidence scope" caveat (paper/docs read, SREGym source not audited).
