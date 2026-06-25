# J6 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — Simulation Correctness (finds: the cascade silently dies)
**Problem found (REAL, caught at runtime):** My first draft wired the victim APIs to the lease
quorum with `pool` edges (matching the "shared finite leases" narrative). But `sim/engine.py`
only propagates error through `_error_edges = required + discovery`. `pool` and `queue` carry
NO error in Tier-A. Result: after inject, `order-api`/`ledger-api` error = **0.0** — no cascade,
`assertions.cascades=true` is a lie, and the whole scenario is inert. The first sim run printed
`"cascades": false, "result": "FAIL"`.
**Fix applied:** victim edges changed `pool → required` ("a valid single leader lease is
*required* to serve writes"). Re-run: victims at 75% error, cascade fires. The `lease-quorum`
node keeps `kind: pool` (harmless; validator only requires `pool_size` when a `pool` *edge*
targets it, and there is none now).

## Engineer 2 — Faithfulness / Honesty (finds: the fix-uniqueness overclaim)
**Problem found (REAL):** The scenario narrative says the cure is `restart_service`, "network
policy on the victims does nothing because the partition is in TIME." But `REMEDIATION['dns_race']
= {modify_network_policy, restart_service}`. So `modify_network_policy` *on the root node*
`chrono-ntp` ALSO resolves in Tier-A. If I assert "only restart works" the spec is unfaithful to
its own engine.
**Fix applied:** the sim driver no longer claims netpol fails. It (a) tests a genuinely-wrong
tool `clear_cache` and right-tool/wrong-target instead, which DO fail, and (b) records
`engine_note_netpol_on_root_resolves: true` as an explicit honesty note. The narrative is
downgraded from "network does nothing" to "the clock-skew framing *prefers* restart_service" and
the caveat is surfaced in 07/09. No overclaim survives.

## Engineer 3 — Reproducibility / Parallel-safety (finds: the model-override no-op)
**Problem found (REAL, caught at runtime):** First agent run died with
`HTTPError 400 ... api.anthropic.com` even though I set `rex.loop._SMALL_MODEL = args.model`.
Cause: `def propose(scenario, fb, model=_SMALL_MODEL)` binds the default at *def-time*, so
reassigning the module global is a no-op and the loop kept calling the dead Anthropic model.
Second latent risk: registering the scenario by writing `registry.json` would corrupt sibling
workers.
**Fix applied:** (a) `propose_fn = functools.partial(propose, model=args.model)` passed into
`refine_loop` — actually overrides the model; (b) registration mutates the in-memory
`rex.harness._SCENARIOS` dict only, never the file. Re-run: all 3 gateway models reach reward
1.0. Also confirmed the P0 *deterministic* judge (default) needs no LLM, so judging never hits
the dead Anthropic endpoint.

## Final filtered spec (deltas folded in)
1. Victim edges are `required` (not `pool`) so the cascade actually propagates.
2. No "only restart works" claim; the netpol-on-root resolution is recorded as an engine caveat;
   negative controls use `clear_cache` (wrong tool) and wrong-target.
3. Model override via `functools.partial`; in-memory registry only; deterministic judge.
4. Everything else (topology, trap, smoking gun, SLOs) unchanged from 04.
