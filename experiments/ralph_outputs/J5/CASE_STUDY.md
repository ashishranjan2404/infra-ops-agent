# Case Study — The Cloudflare WAF-Regex Outage, Run End-to-End Through the Agent

> **Scope up front (N=1).** This is a single, fully-transparent illustrative trace,
> not a benchmark result. It exists to make the *mechanism* legible: how the
> propose→simulate→score→feedback loop diagnoses a loud-alert-≠-root cascade,
> avoids the tempting trap, and reaches the fix.
>
> **Reproducibility metadata.** Scenario `cloudflare_waf_regex`
> (`scenarios/cidg/generated/76-cloudflare-waf-regex.yaml`, `seed: 1076`).
> Proposer = **`gpt-5.5`** via the HUD inference gateway (the default roster model,
> Claude Haiku, was unreachable — Anthropic credits exhausted on this machine — so
> the frozen proposer was routed to a reachable gateway model; the *agent* is this
> frozen LLM in a refinement loop, not a trained policy). Diagnosis judge =
> **deterministic** keyword-set (`REX_JUDGE_MODE=deterministic`, no LLM). Sim =
> Tier-A `sim/engine.py`. Raw trace: `artifacts/trace.json`; trap demonstration:
> `artifacts/trap_vs_fix.json`. Both were produced by
> `artifacts/run_case_study.py`.

---

## 1. The incident

On **2019-07-02** Cloudflare pushed a new managed WAF rule containing a regular
expression with **catastrophic backtracking**. On every edge request the regex
engine blew up to super-linear CPU, pinning processors to 100% across the global
edge and producing a wall of HTTP 5xx. The loudest signal was CPU saturation and
errors on the customer-facing proxies — *not* on the component that actually broke
(the WAF rule engine).

The scenario reproduces that shape. The topology is:

```
edge-proxy  ──required──▶ ingress-gw ──required──▶ waf-engine   (the root)
origin-api  ──required──▶ ingress-gw
```

Every product path runs through the shared `ingress-gw → waf-engine` chain, so a
fault on `waf-engine` surfaces simultaneously as 503s on *all* downstream
products. The alert the on-call actually sees (verbatim from the run's prompt):

```
ALERT firing: 503 error-rate spike across MULTIPLE product APIs (edge-proxy, origin-api) at once.
Observed error_rate_pct (loudest first): edge-proxy 62%, origin-api 57%, api-gateway 40%.
Recent change: a 'edge-proxy' deploy completed ~8 minutes before the spike began
  (rollout reports complete; image bumped a minor version).
Logs (sampled): edge-proxy: 'request failed: 503 from api-gateway';
  api-gateway: 'upstream auth/quota check returned 503' (x hundreds).
Topology: ingress-gw --required--> waf-engine; edge-proxy --required--> ingress-gw;
  origin-api --required--> ingress-gw.
(Note: cloud-service-health monitors waf-engine and the status page is lagging/stale.)
SLO breached: error_rate_pct higher-bad 5 on edge-proxy, origin-api.
```

The incident is laced with two **decoys**: (a) the loudest metric is on
`edge-proxy`, inviting you to scale the victim; (b) a recent `edge-proxy` deploy 8
minutes prior invites a "bad deploy on edge-proxy" theory. Both are wrong. The
status page even monitors the real root and is *stale*, mirroring the real outage.

---

## 2. The agent's reasoning, step by step (real output)

The loop ran for **2 iterations** before a clean win (it stops the moment a plan
has no failed checks; budget was 6 but it did not need them).

### Iteration 0 — correct diagnosis, wrong fix tool

The agent's stated root cause (verbatim from `trace.json`):

> *"waf-engine is returning 503 on the required shared ingress path, causing
> ingress-gw/api-gateway checks to fail and all product APIs to simultaneously
> surface 503s."*

This is the hard part of the cascade, and the agent got it **at iteration 0,
before any feedback**: it reasoned from the topology ("all products fail through a
shared path") to the **upstream** root `waf-engine`, ignoring both the loud
`edge-proxy` metric and the `edge-proxy` deploy red herring. The deterministic
judge scored `diagnosis_correct = true`.

But its proposed action was wrong:

```json
{"tool": "failover_service", "args": {"target": "waf-engine"}}
```

Failing the WAF engine over does not undo the bad rule. The sim left the incident
**unresolved** (`score = 0.3`, `failed_checks = ["correct_fix_missing", "not_resolved"]`).
The loop fed back (verbatim):

> *"ROOT CAUSE: correct ... FIX: your plan did NOT include a remediation that
> targets the real root 'waf-engine'. What resolves it: rollback_deployment on
> waf-engine."*

### Iteration 1 — the fix

With that feedback the agent kept its (correct) diagnosis and switched tools:

> *"A catastrophically-backtracking WAF regex rule deployed to waf-engine is
> pinning CPU on every edge request, causing shared ingress auth/quota checks to
> return 503 across products."*

```json
{"tool": "rollback_deployment", "args": {"target": "waf-engine"}}
```

The sim reports **resolved = true**, `failed_checks = []`, `score = 1.0`. The loop
terminates with `outcome = "resolved"`, `clean_win = true`, `best_iter = 1`.

---

## 3. The trap it avoided

There are **two distinct claims** here; the case study keeps them separate:

**(a) The agent never proposed the trap.** Across both iterations it never
suggested scaling the loud victim `edge-proxy`, despite that being the most
salient metric in the alert. Avoiding the "chase the page" reflex is the
behavioural win.

**(b) The harness would have blocked it anyway.** As a counterfactual, the trap
plan `scale_deployment(edge-proxy, replicas=8)` was run directly through the sim
(`artifacts/trap_vs_fix.json`). Result:

```
TRAP  scale edge-proxy   -> resolved: False
      blocked by is_safe: "scale_deployment blocked for cloudflare_waf_regex:
      it treats 'saturation', a ruled-out cause ..."
FIX   rollback waf-engine -> resolved: True, root_cleared: True
```

The `is_safe` Layer-1 gate refuses the action because `scale_deployment` treats the
`saturation` category, which is in this incident's `forbidden_categories`. Note —
honestly — that "scaling does not resolve" is **by construction**: the reward
function encodes that scaling a CPU-saturation symptom cannot clear a `bad_deploy`
root. It is a *designed* safety property of the environment, demonstrated here, not
an empirical discovery.

---

## 4. The fix and the outcome

| | Iter 0 | Iter 1 |
|---|---|---|
| Stated root | waf-engine (upstream) ✅ | waf-engine, names the regex ✅ |
| Action | `failover_service(waf-engine)` | `rollback_deployment(waf-engine)` |
| Diagnosis correct | ✅ | ✅ |
| Resolved | ❌ | ✅ |
| Score | 0.30 | 1.00 |
| Failed checks | `correct_fix_missing`, `not_resolved` | none → **clean win** |

The fix mirrors Cloudflare's actual remediation: **roll the bad WAF rule back**.
Final outcome: incident **resolved**, root cleared, no trap executed, no unsafe
action attempted — in **2 iterations**.

---

## 5. What this case study shows (and doesn't)

**Shows.** The agent's competence and the harness's safety are *separable and both
real*: the frozen proposer independently diagnosed the upstream root at iter 0
(the harness did not supply that), and the `is_safe` gate independently guarantees
the loud-victim scaling trap can never resolve the incident. The feedback loop
converted a correct-diagnosis/wrong-tool plan into the canonical fix in one step.

**Doesn't / limitations.**
- **N=1, single sample.** One realized trace; the proposer is stochastic. Only the
  *grading* (deterministic judge + sim) is reproducible. Iteration count is not a
  metric.
- **Prompt hint.** The cascade prompt explicitly nudges "it may be UPSTREAM ... ALL
  products are failing through a shared path." The agent deserves credit for *using*
  that correctly, not for discovering upstreamness unaided.
- **Deterministic keyword judge.** "Diagnosis correct" is keyword-set overlap, not
  semantic understanding; read the quoted sentences and judge for yourself.
- **Trap branch is by-construction**, as stated in §3.
- **Model swap.** The proposer is `gpt-5.5` (gateway), not the default roster Haiku,
  because Anthropic credits were exhausted. "The agent" in this run is that model.
