# J6 — 07 Test Results

## T1 — YAML validation (`python3 -m sim.spec validate`)
```
$ python3 -m sim.spec validate scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml
OK    scenarios/cidg/generated/90-chronos-ntp-lease-splitbrain.yaml  [chronos-ntp-lease-splitbrain]  4 nodes / 3 edges / rc=dns_race

1/1 specs valid
```
**PASS** — parses, in closed vocab, all structural assertions satisfied (cascades has
required/discovery edges; buried_gun present).

## T2–T6 — Sim engine generalization (`run_novel_sim.py`, exit 0)
From `artifacts/sim_result.json`:
```json
"after_inject":  {"order-api": 75.0, "ledger-api": 75.0},   // T2 cascade fires  PASS
"resolved_after_inject": false,                              //    not auto-resolved
"after_trap":    {"order-api": 75.0, "ledger-api": 75.0},
"resolved_after_trap": false,                               // T3 trap ¬resolve   PASS
"resolved_after_wrong_tool_clear_cache": false,            // T4 wrong tool      PASS
"resolved_after_right_tool_wrong_target": false,           // T5 wrong target    PASS
"after_fix":     {"order-api": 0.0, "ledger-api": 0.0},
"resolved_after_fix": true,                                 // T6 canonical fix   PASS
"engine_note_netpol_on_root_resolves": true,               // honesty caveat (see below)
"result": "PASS"
```
All 5 boolean checks True. The cascade multiplies the root's 0.75 own-error through the
`discovery`→`required` chain to **75%** error on both victim APIs; only `restart_service`
on `chrono-ntp` drives them back to 0.

### Recorded engine caveat (NOT a failure)
`engine_note_netpol_on_root_resolves == true`: because `REMEDIATION['dns_race']` also contains
`modify_network_policy`, running it on the ROOT node likewise resolves in Tier-A. The scenario
narrative *prefers* `restart_service` (clock re-sync) but does not — and cannot, given the
shared engine physics — make network-policy "do nothing." Surfaced honestly per the ouroboros
self-critique; the canonical fix and the negative controls are unaffected.

## T7 — Agent path, 3 frozen models (`run_novel_agent.py`)
Env: `set -a; source ~/.zshrc; set +a` (HUD_API_KEY). Anthropic direct calls are out of credits
(400), so the loop is routed to HUD-gateway models. P0 *deterministic* judge (no LLM judge).

| model | result | reward | resolved | clean_win | iters | diagnosis_correct |
|-------|--------|--------|----------|-----------|-------|-------------------|
| glm-5p2        | PASS | 1.0 | true | true | 2 | true |
| minimax-m3     | PASS | 1.0 | true | true | 2 | true |
| deepseek-v4-pro| PASS | 1.0 | true | true | 2 | true |

Example final plan (glm-5p2): `[{restart_service, target: chrono-ntp}]`, stated root cause
*"The chrono-ntp time source skewed +1100ms, causing the leader lease to read as expired … split-brain
across all products sharing the lease-quorum path."* — correct diagnosis, correct fix, no trap.

## Fixes applied during testing (full audit trail in 05)
1. **Inert cascade** — victim edges `pool → required` (pool carries no error in Tier-A). Re-run: 75%.
2. **Model override no-op** — `_SMALL_MODEL` reassignment ignored (def-time default); switched to
   `functools.partial(propose, model=...)`. Re-run: gateway models reached.
3. **Overclaim** — dropped "network does nothing"; recorded the netpol-on-root caveat; used
   `clear_cache`/wrong-target as the real negative controls.

## Net
Validation PASS · sim PASS (5/5 + caveat) · agent PASS (3/3 models, reward 1.0).
