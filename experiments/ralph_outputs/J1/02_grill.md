# J1 — 02 Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (AAAI)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR:** The interesting claim is that REAL chaos produces the *same emergent
cascade* as `sim/engine.py`. If true, an agent trained/evaluated in sim transfers
to infra. I want the live and offline graders to be literally the same function,
or the transfer claim is unfalsifiable.

**PSRE:** Operationally my only hard requirement: chaos must auto-heal and never
escape the namespace. HTTPChaos with `abort:true` on payments is a clean root-cause
signal. But `mode: all` on payments hits both replicas — defensible (LB would mask
a single-replica fault) but say so. Also: you're injecting at L7 (HTTPChaos) AND
the app already has `/ctl/fault`. Pick a lane or you'll double-fault.

**AAAI:** A harness that grades against a 5-item hand-written GROUND_TRUTH is a toy.
Where's the baseline? What does "the agent" even score vs a trivial
"always-blame-loudest-victim" heuristic? Without that contrast the deliverable is an
engineering demo, not an evaluation.

**RLE:** I care that the observation schema the agent sees is identical across
backends, else the policy sees distribution shift between train (sim) and eval
(kube). The `Observation` dataclass has to be backend-invariant.

**DOL:** Who can run this? The Job needs RBAC to create Chaos Mesh CRs. If you give
it cluster-admin you've built a foot-gun. Least-privilege Role scoped to the
namespace, and it must be able to *delete* chaos (heal) but never delete workloads.

## Round 2 — react to another persona (genuine disagreement)

**PSRE → SMR:** I disagree that live and sim "must be the same function" end-to-end.
The *grader* should be shared, yes. But forcing the *observation* to be identical is
wrong — the whole point of going to infra is that real metrics are messier (LB
jitter, scrape gaps, partial pod failures). If you sand that off to match sim, you've
defeated the reason to leave sim. Keep the schema shared but let kube carry `None`s
and noise.

**SMR → PSRE:** Fair, and that actually strengthens my transfer claim if the policy
survives the noise. Concede.

**AAAI → RLE:** "Backend-invariant observation" is over-engineering for what is a
*systems* deliverable, not a learning run. There's no policy being trained here. You're
importing RL hygiene into a deployment task. The risk isn't distribution shift, it's
that the harness never actually touches a cluster — which is exactly what's about to
happen.

**RLE → AAAI:** Pushing back hard — this project's entire framing (per repo notes) is
code-as-policy / auto-harness with a frozen LLM. The harness IS the eval substrate. If
the obs schema drifts, every downstream REx comparison is contaminated. Not over-eng;
it's the one thing that must be right.

**DOL → PSRE:** You said "pick a lane: HTTPChaos vs /ctl/fault." I disagree — keep BOTH
but for different purposes. `/ctl/fault` is the app-internal smoke test (no Chaos Mesh
needed); HTTPChaos/NetworkChaos/StressChaos are the *infra* faults that exercise the
real kubelet/CNI path. They're complementary fidelity levels, not a conflict. Document
them as a ladder.

**DOL → AAAI:** And you're right that there must be a baseline; the harness should ship
the "always-blame-loudest-victim" agent as the trivial baseline so any real agent has
something to beat.

## Round 3 — synthesis

Consensus reached:
1. **Shared grader, not shared observation.** Both backends call
   `rex.scoring.deterministic_judge`; the `Observation` schema is shared *in shape*
   but `kube` is allowed to carry `None`/noise (PSRE+SMR win over a rigid RLE).
2. **Fault ladder, documented:** L0 `/ctl/fault` (app smoke), L1 Chaos Mesh infra
   faults. Both kept; not a conflict (DOL).
3. **Baseline required:** ship the loudest-victim heuristic as the agent-to-beat, and
   red-herring lists so the grader penalizes blaming the victim (AAAI).
4. **Safety is non-negotiable:** namespace-scoped, time-bounded, `finally`-delete,
   least-priv RBAC that can heal but not delete workloads (PSRE+DOL).
5. **Honesty about the cluster:** the single biggest risk is "never touches infra." If
   live access fails, that must be reported as a precise blocker, not hidden behind a
   green sim run (AAAI).
