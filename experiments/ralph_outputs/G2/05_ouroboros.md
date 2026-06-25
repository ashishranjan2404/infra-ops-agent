# G2 — Ouroboros (3 self-critiques, each finds real problems)

## Engineer A — "the target-resolution bug hunter"
**Problems found:**
1. **Target extraction from kubectl is fragile.** `kubectl scale deploy/foo --replicas 5`
   vs `kubectl scale deployment foo --replicas=5` vs `-n ns deploy/foo` — naive split
   will mis-extract. If the target doesn't match a node name, the fix silently no-ops and
   the scenario "fails" for a *parsing* reason, inflating the apparent Stratus failure
   rate. -> Must strip `deploy/`, `deployment/`, `pod/`, `-n <ns>`, and `=`-joined flags,
   then match against `spec` node names; if no match, mark `untranslated` (honest) rather
   than guessing.
2. **`is_resolved` needs the fault node as the action target.** `sim.engine.apply_action`
   only clears the root if `target == world._fault_node`. If kubectl target resolves to a
   *victim* node (the loud one), the correct tool still won't resolve. That's actually
   faithful (right tool, wrong target fails) — but the adapter must surface the resolved
   target so the fidelity report distinguishes "wrong reasoning" from "lost target".

## Engineer B — "the scope / over-engineering critic"
**Problems found:**
3. **Traces family is near-useless and risks implying false fidelity.** Jaeger traces in
   SREGym are rich; our "traces" are just edges with summed latency. Shipping it as if
   it's comparable oversells the adapter. -> Keep it but explicitly label it
   `low_fidelity: true` in the return and in the brief; don't pretend it's Jaeger.
4. **Two-metric observation under-serves Stratus.** Real Stratus reads dozens of
   Prometheus series; ours has `error_rate_pct` + `p99_latency_ms`. This is a genuine
   fidelity ceiling, not a bug — but it MUST be stated as a blocker-adjacent limitation,
   else a reviewer thinks we hid it. -> Documented in 09_critique + brief.
5. **The line/JSON-RPC protocol is over-specified for the proof.** We don't need a live
   socket server to prove the loop; an in-process `SREGymEnv` driven by an external-style
   stub is sufficient and avoids a flaky network dependency. -> Implement the class; note
   the socket wrapper as a 1-function extension in RUN_PLAN, don't build/flake it.

## Engineer C — "the falsifiability / honesty auditor"
**Problems found:**
6. **Diagnosis grader could rubber-stamp.** A keyword check that's too loose marks any
   text mentioning the node as correct. -> Require BOTH the fault-node substring AND a
   kind keyword; add a negative test (off-topic string must score False) so the grader is
   demonstrably falsifiable.
7. **The stub must be able to FAIL.** If the stub always passes, the adapter is unfalsified
   (AAAI's R2 point). -> Add the explicit trap run: a non-remediating tool yields
   `resolved=False` from the real engine. This proves the verdict comes from `sim.engine`,
   not from the stub.
8. **Don't imply we ran Stratus.** Every artifact must say Stratus was NOT executed here;
   the blocker is first-class. -> Headers in RUN_PLAN + STRATUS_BRIEF + result.json
   `blocker` field.

## Final filtered spec (deltas applied)
- Robust kubectl target parser: strip `deploy/|deployment/|pod/|node/` prefixes, drop
  `-n <ns>` and `=`-joined flag values, match remaining bare token against node names;
  no match => `untranslated`.
- `cluster_control` returns the **resolved target** + whether it matched a node.
- `get_traces` returns `{"low_fidelity": True, "spans": [...]}`.
- Diagnosis grader requires node-substring AND kind-keyword; covered by a negative test.
- Stub runs BOTH a solve and a trap; both verdicts come from `sim.engine`.
- No live socket server; in-process env + external-style stub; socket noted as a stub-
  swappable extension in RUN_PLAN.
- Every doc states Stratus was not run + names the exact blocker.
