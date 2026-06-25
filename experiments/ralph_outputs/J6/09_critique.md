# J6 — 09 Critique (honest)

## What a reviewer attacks first

1. **"Novel" is constrained by a closed vocab.** The strongest objection: the scenario's
   `root_cause.kind` is `dns_race`, a kind the models have solved before. So this tests
   generalization to a novel *mechanism/topology/narrative*, **not** a novel *fault class*. A
   true held-out-kind test (a kind token absent from training) is impossible here — `sim/spec.py`
   rejects out-of-vocab kinds, and the engine has no physics for an unknown kind. I claim
   mechanism-level novelty, which is real but weaker than class-level novelty. Stated plainly.

2. **N = 1 scenario.** One hand-authored incident cannot establish "the agent generalizes" as a
   population claim. I mitigated with 3 distinct frozen models (so it's not a single-policy
   fluke) and full negative controls (trap/wrong-tool/wrong-target all fail). But the honest
   scope is: *on this one novel incident, three frozen policies generalize cleanly.*

3. **The task may be too easy.** All 3 models hit reward 1.0 in ≤2 iterations → zero within-group
   spread, which by the HUD task-design doctrine is *untrainable* (no gradient). The smoking gun
   names the root almost verbatim and the gold_root NL is descriptive. As a *generalization
   probe* this is fine (we want to know IF it transfers), but as a *training* item it would need
   harder distractors / a more buried gun to create spread. Noted, not fixed (out of J6 scope).

4. **Engine faithfulness gap (the netpol caveat).** `REMEDIATION['dns_race']` admits
   `modify_network_policy`, so the "TIME not network" narrative is not enforced by Tier-A — a
   wrong-theory-right-node netpol action would also resolve. I recorded this rather than hiding
   it, but a purist would say the scenario's discriminating story is only half-modeled by the
   fast sim (it would hold better on the live mesh / with a custom REMEDIATION, which I must not
   edit). This is the weakest point of the deliverable.

5. **Tier-A only; no hysteresis.** The realistic incident needs clock-fix THEN lease-restart
   (two steps); Tier-A collapses this into one `restart_service`. I set `persistent: false` to
   match the engine. So the "split-brain leases survive the clock fix" subtlety is documented
   narrative, not simulated behavior.

## What's genuinely solid
- The scenario is real, valid, and runs end-to-end through both the ground-truth engine and the
  real frozen-LLM agent loop, with reproducible commands.
- Parallel-safety is airtight: no shared-core or registry file was written.
- The result is honestly a *positive* with its limits disclosed, plus negative controls that
  rule out the trivial "any plan wins" explanation.

## If I had more budget
- Author 3–4 sibling NTP/time-skew variants (different topologies, buried guns, a paired-positive
  where scaling IS correct) to get a within-family spread and a population-level claim.
- Propose (as a `.patch`, not an edit) splitting `dns_race` remediation so clock-skew ≠ netpol,
  to close the faithfulness gap.
- Add a genuinely harder gun (offset reported only in a trace percentile, not a log line).
