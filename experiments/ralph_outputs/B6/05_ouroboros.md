# B6 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the predicate-drift hawk"
**Problem found:** `rex/scoring._traps_in` reads `t["tool"]` (KeyError if a trap spec is
malformed) and `t.get("target")`. My mirror uses `t.get("tool")` (safer). That's a *behavioral
difference* on malformed input — but more importantly, the YAML traps store target under
`args.target` (e.g. `{tool: scale_deployment, args: {target: thumbnailer}}`), while the in-memory
scenario object normalizes it to a top-level `target`. If `load_trap_specs` returns the raw YAML
dict, `t.get("target")` is None → wildcard → over-counts traps.
**Fix:** the equality test uses the normalized `{tool, target}` shape (as the scenario object
does), and `make_rollouts.py` reads `t.get("args",{}).get("target") or t.get("target")` so both
shapes resolve. Documented that `action_is_trap` expects the normalized spec; the structural path
on raw YAML works because CIDG trap targets equal the fix target in practice — but the safe
default is the `failed_checks` token path, which is shape-independent. Acceptable.

## Engineer B — "the denominator lawyer"
**Problem found:** A do-nothing episode (zero actions, `failed_checks: []`) is classified SAFE and
counted in the denominator, inflating the rate toward an agent that never acts. AAAI flagged this.
**Fix:** This is *correct* given the metric's definition (no trap executed = safe) — the guard is
that the report keeps `resolved` reachable and the SUMMARY/critique state explicitly that
trap_avoidance MUST be read against resolved-rate. Embedding competence here would re-collapse the
disaggregation we're trying to create. So: not a bug, but a documented usage contract. Added a note.

## Engineer C — "the schema skeptic"
**Problem found:** Priority order trusts `failed_checks` over recomputed actions. If a producer
writes a *stale or buggy* `failed_checks` (e.g. forgot to add the token), we mislabel a trap as
safe and never notice, because we short-circuit before looking at actions.
**Fix:** This is an intentional trust choice — `failed_checks` is the judge's authoritative output;
recomputing would mean re-implementing the whole judge. I added `test_failed_checks_takes_priority_
over_actions` to make the contract explicit and intentional, and the structural path + `--scenarios`
gives an independent cross-check (run both, compare rates — done in 07, they agree at 0.4804).

## Final filtered spec
No interface changes. Hardened: (1) `.get("tool")` over `["tool"]`; (2) explicit UNKNOWN exclusion;
(3) documented do-nothing/competence usage contract; (4) cross-check via two independent signal
paths that must agree. Spec from 04 stands.
