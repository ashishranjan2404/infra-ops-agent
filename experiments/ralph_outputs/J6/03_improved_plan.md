# J6 — 03 Improved Plan

## What changed after the grill

### Accepted
1. **Add negative controls (REV, RLE).** The sim driver now checks *four* failure modes, not
   just "fix resolves": (a) cascade present after inject, (b) trap `scale_deployment order-api`
   does NOT resolve, (c) genuinely-wrong tool `clear_cache chrono-ntp` does NOT resolve,
   (d) right tool / WRONG target (`restart_service order-api`) does NOT resolve. Only then does
   (e) the canonical fix resolve. This rules out "any plan wins."
2. **≥3 frozen models on the agent path (REV).** Run `glm-5p2`, `minimax-m3`, `deepseek-v4-pro`
   so a clean win is not a single-policy artifact.
3. **In-memory registration only (DVO, RLE).** Register the novel scenario in
   `rex.harness._SCENARIOS` at runtime; the shared `registry.json` on disk is never written.
   Same `load_scenario → refine_loop` code path, fully parallel-safe.
4. **Honest engine caveat (SMR R2).** `REMEDIATION['dns_race']` also contains
   `modify_network_policy`, so on the ROOT node Tier-A would also resolve via netpol. The
   "network does nothing" framing is a *narrative* claim about the live mesh, NOT enforced by
   Tier-A. The sim driver records this as `engine_note_netpol_on_root_resolves` rather than
   pretending it fails.

### Rejected (with reason)
- **SMR R1 "a dns_race win is just token lookup":** rejected. The agent never receives the
  kind token; it gets an NL alert and must *write* a diagnosis that the deterministic judge
  compares to the gold NTP description. The trap is the network red herring and the textbook
  `dns_race→modify_network_policy` reflex points at a *victim*. So parsing the clock narrative
  is exactly what is tested. (PSRE R2 rebuttal accepted.)
- **PSRE R1 "single restart_service is unfaithful (should be clock-then-restart)":** rejected
  for Tier-A. The fast engine does not model hysteresis (`apply_action` clears the root when the
  correct tool hits the fault node), so a single `restart_service` IS the faithful Tier-A fix.
  The two-step real-world story is documented as a live-mesh nuance, not graded by the fast sim.

## Final plan (unchanged scaffold, hardened checks)
1. Author YAML with `dns_race` kind, `control_plane` time source, `discovery` edge to the lease
   service, `required` edges from the two victim APIs (so error multiplies through), trap =
   scale loud victim, fix = `restart_service chrono-ntp`.
2. `python -m sim.spec validate` → must be clean.
3. Sim driver: 5 checks (cascade, ¬trap, ¬wrong-tool, ¬wrong-target, fix-resolves) + engine note.
4. Agent driver: in-memory register, 3 gateway models, P0 judge, reward ≥ 0.8 = generalizes.

## Success criteria (sharpened)
- `validate()` == `[]`.
- Sim: all 5 boolean checks True; engine caveat recorded.
- Agent: ≥1 (ideally all 3) frozen models reach reward ≥ 0.8 with correct diagnosis and no trap.
