# G2 — Honest Critique

## The headline weakness
The task asks to "run our benchmark with Stratus." We did NOT run Stratus. We built the
machinery that would let it run and proved that machinery with a stub. A hostile reviewer
will say: "this is the reverse comparison without the comparison." That is fair. What we
deliver is *infrastructure + a documented blocker*, which is the honest ceiling given no
vendored Stratus, no MCP transport, and the sandbox. It is real, but it is not the number.

## Where a reviewer attacks the adapter
1. **Action-distribution confound (the deepest issue).** Stratus emits free-form `kubectl`
   and parses `kubectl get -o yaml`. Our world has no YAML objects and a 25-verb menu. The
   `untranslated_kubectl_rate` *measures* this gap but does not *close* it. On cascade-heavy
   scenarios the rate could be high enough that any Stratus result is interface-bound. We
   scope the claim to 1:1-faithful leaf scenarios, but that shrinks the comparison surface.
2. **Two-metric observation ceiling.** Real Stratus reads dozens of Prometheus series; we
   expose two (`error_rate_pct`, `p99_latency_ms`). A frontier agent starved of signal will
   underperform for *observability* reasons, not reasoning — confounding any "Stratus fails
   on our benchmark" claim. This is a genuine fidelity ceiling, not a bug.
3. **3 scenarios don't even run.** `is_resolved` raises `KeyError` on SLOs referencing
   `pod_restarts` / `cpu_utilization_pct` / `latency_p99_ms`. We excluded them honestly,
   but it reveals our own engine/SLO surface is inconsistent — a finding that slightly
   undercuts "our benchmark is a clean target."
4. **Diagnosis grader is a keyword check, not the LLM judge.** Kept dep-free for the
   scaffold, but it can both false-pass (text that happens to contain node+keyword) and
   false-fail (a correct paraphrase using synonyms). Real runs must swap in `rex.scoring`'s
   judge.
5. **TNR is not really emulated.** Stratus's Transactional No-Regression safety loop wants
   to probe the live cluster between steps and revert regressions. Our adapter supports
   re-reading metrics after each action but has no revert primitive, so Stratus's signature
   safety mechanism is only partially exercisable.

## What's missing
- The MCP/HTTP transport server (the one piece between "verified in-process adapter" and
  "Stratus actually connects"). Deliberately not built (unverifiable in sandbox) but it is
  the critical path.
- Any real Stratus output, and therefore any actual reverse-comparison number.
- A faithfulness audit quantifying, per scenario family, how lossy the kubectl mapping is.

## What's genuinely solid
- The adapter runs 58/61 scenarios and returns real engine verdicts; the loop is proven
  falsifiable (trap fails, negative diagnosis fails). The SREGym registration matches the
  documented schema. The brief is sourced. The blocker is specific and unblockable with a
  named, finite checklist. This is a credible "blocked-but-completed-deliverable" result,
  not vaporware — but it is one transport-shim and one cluster-of-keys away from the real
  number, and that distance should not be understated.
