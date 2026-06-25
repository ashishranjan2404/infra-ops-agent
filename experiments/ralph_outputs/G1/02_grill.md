# G1 — Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial takes

**SMR:** The valuable thing here is the *comparison axis*. SREGym's New partition
(n=13) is exactly the "novel failure" regime where every leaderboard agent
collapses (E2E 60.8 -> 28.2 for Claude Code). Our whole thesis is the
novelty-router / escalation handoff. So the right experiment isn't "beat the
leaderboard average," it's "on the New partition, does our escalate-instead-of-
hallucinate behavior reduce harmful mitigations?" That's a sharper, more honest claim.

**PSRE:** From an operator's seat, the part that worries me is the **mitigation
oracle**. SREGym verifies the *real system recovered*. Our agent emits
`scale_deployment(target=...)`. On a live cluster that's a `kubectl scale deploy`.
Fine. But for a cascade where the real fix is "disable a bad network policy path,"
our `modify_network_policy` tool is an abstraction — there is no generic kubectl
that knows which policy to write. The translation is lossy and the oracle will
catch it. We must be honest that mitigation pass-rate is the hard wall.

**AAAI:** Methodologically, a direct leaderboard comparison is only valid if the
*agent harness* is matched. SREGym runs agents in isolated Docker containers with
MCP tools and a real observe loop. Our agent is single-shot plan emission over a
simulator. If you "compare" a single-shot planner to a multi-turn tool-using agent,
reviewers will reject it as apples-to-oranges. Either you (a) wrap our policy in a
genuine multi-turn agent, or (b) frame it explicitly as a *transfer/zero-shot*
result with caveats. Do not paper over the harness asymmetry.

**RLE:** Engineering reality: the adapter is the deliverable, and it has two halves.
Half one (diagnosis) is easy — our `root_cause` string drops straight into O_d's
NL judge. Half two (mitigation) requires translating our fixed tool vocabulary into
kubectl/MCP calls AND knowing the target namespace/resource names, which come from
the live problem, not from us. So the adapter MUST be parameterized on the live
cluster's resource catalog; a pure offline scaffold can validate the *contract* but
not the *binding*. Be clear about that boundary.

**DOL:** None of this runs here. No kind, no Docker daemon guaranteed, no Helm 4,
no Ansible cluster, and SREGym wants Python >= 3.12 + uv + recursive submodules.
Standing up even the kind path is a multi-hour, multi-GB job with GPU/arch caveats
(x86 vs arm). The deliverable has to be a scaffold + run plan + blocker. Anyone who
claims they ran 90 live problems in this session is fabricating.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**PSRE -> SMR:** I disagree with SMR's "just measure escalation on the New
partition" framing being clean. Escalation is only virtuous if the agent *also*
isn't escalating the 77 problems it COULD solve. If our agent escalates everything,
its "no harmful mitigation" score is trivially perfect and meaningless. The metric
must be paired: harmful-mitigation-rate AND solve-rate. SMR's single-axis story is
too flattering.

**SMR -> PSRE (pushback):** PSRE is right that escalation needs a denominator, but
PSRE is overweighting the mitigation oracle as "the hard wall." For a *research*
contribution, diagnosis quality on novel faults is itself publishable — fault
localization (originating component vs cascade victim) is the exact thing our
cascade scenarios train. I reject the idea that mitigation pass-rate is the only
number that matters; O_d is graded independently by SREGym for precisely this reason.

**RLE -> AAAI (sharp disagreement):** AAAI says wrap our policy in a "genuine
multi-turn agent" or the comparison is invalid. I disagree that this is required for
*this* task. Our agent's contribution is the *plan policy* (REx tree + novelty
router), not a tool-using scaffold. The honest move is to expose our policy through
SREGym's interface as-is and label it "non-interactive planner baseline." That's a
legitimate, citable point on the leaderboard ("how far does a pure planner get?"),
not an invalid comparison — as long as we *say* it's non-interactive.

**AAAI -> RLE (holds ground):** I hear RLE, but a "non-interactive planner baseline"
that never reads metrics/logs/traces is not solving the same task — SREGym problems
are *designed* so the root cause is only discoverable by querying observability.
Feeding our agent a pre-baked alert snapshot (as our `build_prompt` does) leaks
structure SREGym deliberately withholds. So the adapter MUST, at minimum, gather a
real observation bundle (metrics/logs) and feed THAT to our proposer, or the result
is contaminated. This is non-negotiable for validity.

**DOL -> RLE:** RLE's "parameterize on the live resource catalog" is correct but
understates it. The target names (`deployment/checkout`, namespace `social-network`)
differ per problem and per app (Kubernetes vs TiDB vs Kafka). The translator can't
be a static dict; it needs a discovery step (`kubectl get deploy -A`) at run time.
The offline scaffold should therefore ship a *resolver interface* with a stub, not
pretend it has the mapping.

## Round 3 — synthesis

Consensus the personas converged on:
1. **Frame honestly as a non-interactive-planner transfer result**, explicitly
   labeled, NOT a like-for-like leaderboard claim (AAAI + RLE compromise). Add the
   caveat that SREGym agents are interactive tool-users.
2. **Validity fix (AAAI, accepted):** the adapter must feed our proposer a real
   observation bundle gathered from the live cluster's MCP servers, not a pre-baked
   snapshot, so we don't leak withheld structure. The scaffold ships an
   `ObservationGatherer` interface with a documented stub.
3. **Paired metric (PSRE, accepted):** report solve-rate AND harmful-mitigation-rate
   AND escalation-rate together; never escalation in isolation.
4. **Mitigation is the hard wall (PSRE):** be explicit that our fixed 12-tool action
   space cannot express many SREGym mitigations; mark out-of-action-space problems
   as N/A, do not score them 0 silently.
5. **Dynamic target resolution (DOL, accepted):** translator takes a runtime
   resolver (`kubectl get`), shipped as an interface + stub; the static map is only
   the *tool semantics*, not the *resource binding*.
6. **The deliverable is scaffold + run plan + blocker** (DOL); no fabricated scores.

Rejected: SMR's single-axis "escalation only" story (too flattering — PSRE won).
Rejected: a fully static translation dict (DOL won — needs runtime discovery).
