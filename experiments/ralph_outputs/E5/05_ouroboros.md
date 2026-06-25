# E5 — Ouroboros (3 self-critiques of the spec)

## Engineer A — "the selection is silently leaky"
**Problem:** The brief says "novel" but `select_novel_set` back-fills with held-out
*simple* incidents (`auth_cert_expiry`, `billing_disk_fill`, `checkout_bad_rollout`)
once the 8 novel-family ones run out. A blended pass@1 over 10 mixes easy leaf incidents
with hard cascades and overstates "generalization."
**Fix accepted:** Keep n=10 (the brief asks for 10) but (a) rank novel-family first so
the simple ones are explicitly the tail, (b) persist `family` per key via the A8 source
so the report is *family-decomposable*, and (c) call this out in `08`/`09`. The per-incident
reward map in `transfer_results.json` makes any per-family recompute trivial.

## Engineer B — "oracle ceiling could mask a broken incident"
**Problem:** `oracle_plan` uses `sorted(correct_fix_tools)[0]` + `fault_node`. If an
incident needs a *multi-step* fix or a non-default fix tool, the single-tool oracle
might not resolve it, silently dragging `ceiling_ok` to false — or worse, a poorly
chosen first tool could still pass via partial credit and hide the gap.
**Fix accepted:** Add an explicit `ceiling_ok` gate (oracle pass@1 must == 1.0). The run
confirms oracle == 1.0 on all 10, so every selected incident is provably solvable under
this harness; if it had failed, the offending incident would be flagged rather than
producing a garbage policy pass@1. Documented as a data-validity control, not a model
ceiling.

## Engineer C — "blocked policy handling is half-specified"
**Problem:** The first draft resolved the LLM client eagerly and would crash `main()` if
the fireball name was bad, killing the whole run (including the valid baseline numbers).
Also a *reachable-but-empty* model (gpt-5.5 returned '') would look like a 0-pass policy
rather than a blocked one.
**Fix accepted:** (1) `make_llm_propose` resolves the roster name in a try/except in
`main`; an unknown name → `status=blocked`, `error="not in ROSTER"`, and the run
continues. (2) `run_policy` wraps each episode; the first transport error marks the
policy blocked with the error string instead of fabricating a number. Empty completions
parse to an empty/zero plan (honest low score), and a hard transport failure is recorded
as blocked — the two are distinguished by `status`.

## Final filtered spec (deltas folded in)
- Selection: novel-first, simple back-fill, assert loadable, persist family.
- Controls: `empty` floor gate + `oracle` ceiling/validity gate.
- Robustness: per-policy and per-episode try/except; blocked != fabricated != zero.
- Output: per-incident reward map for family-level recompute; `floor_ceiling` block.
