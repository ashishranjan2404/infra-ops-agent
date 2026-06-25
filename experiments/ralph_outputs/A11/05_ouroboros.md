# A11 — 05 Ouroboros (self-critique, 3 engineers in sequence)

## Engineer 1 — finds: the "same root cause" claim is under-enforced
Problem: defining root-cause identity by `failure_class` + fix tool is necessary
but the two YAMLs could *also* coincidentally differ in something that secretly
changes the cause (e.g. `root_cause.hidden` or `persistent`). If B set
`persistent:true`, its fix wouldn't stick and it'd be a different problem.
Action: keep `persistent:false` and `severity:0.7` identical across both variants
of every pair; only `hidden` flips (visible leaf vs buried cascade) — and `hidden`
is an observability property, not a cause property. Documented; verified in YAML.

## Engineer 2 — finds: difficulty confound is acknowledged but not measurable yet
Problem: the manifest labels A=leaf, B=cascade but gives no quantitative difficulty
proxy, so a downstream analyst still eyeballs it. Also: all three A-variants are
leaf and all three B-variants are cascade, so "direction" and "difficulty" are
perfectly correlated across pairs — a within-pair control exists but a cross-pair
one does not.
Action (partial): the `cascades / loudest_alert_not_cause / buried_gun_exists`
booleans in each YAML ARE the difficulty proxy and are machine-readable, so the
analyst can filter on them. Honest limitation: with only 3 pairs we can't fully
decorrelate; noted in 09_critique as a scale limitation. Not over-engineering a
4th "cascade-A / leaf-B" pair now — that's a follow-up.

## Engineer 3 — finds: untested integration edge + naming
Problems: (a) Are the chosen fix tools actually in the sim's tool vocabulary, or
just in other YAMLs? (b) Do `kind` values (lb, datastore, service) match what the
loader accepts? (c) Filenames must not collide and should sort after existing 79.
Action: (a)+(b) every tool (restart_service, renew_certificate,
increase_memory_limit) and every node kind used here already appears in shipped
scenarios (verified by grep), so the loader/judge already handle them. (c) numbers
80-85 are unused (dir tops out at 79); generator has a refuse-if-exists guard.

## Final filtered spec (deltas applied)
- Hold `persistent:false`, `severity:0.7` identical within each pair (Eng1).
- Expose difficulty via the existing assertion booleans; accept 3-pair scale limit
  as a documented weakness (Eng2).
- Restrict to already-shipped tools + node kinds; numbers 80-85; refuse-if-exists
  guard (Eng3).
