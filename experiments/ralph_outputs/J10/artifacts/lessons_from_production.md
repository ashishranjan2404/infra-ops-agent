# Lessons from (Pre-)Production: A Deployment-Readiness Analysis

## 0. What "production" means here — and why this is honest

The REx agent has **not** run in a live production environment. It has never been on call, never
held write access to a live cluster, and has never proposed or executed a remediation
against a real incident. There is no shadow-mode telemetry and no real-incident MTTR
measured end-to-end through the loop. This section therefore makes **no claim of
production experience** and reports **no production metrics**. "Lessons" here means two
things, both defensible: (a) what genuinely transfers from the simulation and evaluation
work we *did* do, and (b) the concrete deployment-readiness gaps that real production
would have to close — stated as experiments with acceptance gates, not as results.

Every quantitative claim below traces to an artifact in this repository
(`experiments/ralph_outputs/<TASK>/`). Anything not yet measured is labeled
`TARGET — NOT YET MEASURED`.

## 1. Lessons that transfer from simulation and eval

Here is what we can actually defend.

### L1 — The action layer is the binding safety constraint
The diagnosis can be perfect and the deployment can still be catastrophic, because the
*fix* is what touches the cluster. The scoring/safety harness (`rex/scoring.py`) encodes
this: a `trap_action` (e.g. `restart_service` on a crash-looping control plane, which
herds the datastore; or `scale_deployment` against a per-process leak, where every new
replica OOMs identically) carries a large penalty and some actions are hard-BLOCKED by a
safety harness. The lesson that transfers: **safety must be enforced at the action layer,
independent of how confident or correct the diagnosis looks.** A high-quality root-cause
string is not a license to act.

### L2 — The reward is a gameable proxy, and that is an action-safety problem  [D13]
An adversarial probe over 42 scenarios × 7 attacks (294 probes;
`experiments/ralph_outputs/D13/`) found **5 working ways to fool the deterministic
diagnosis judge**: negating the gold answer (100% fool-rate — "not" is a stopword),
emitting a single gold token with no mechanism (100%), naming the right mechanism on the
wrong component (100%, no component binding), a **hedge** that names the gold cause plus
every red herring at once (92.9%), and homoglyph evasion of the herring penalty (85.7%).
The hedge is the dangerous one: a hedge diagnosis combined with a *legitimate* correct fix
scores **0.55** on the real `score_plan` in 38/42 scenarios.

Why this is an action-safety lesson, not just a reward-integrity curiosity: the policy
learns its action distribution from the reward. A reward that pays 0.55 for non-committal,
hedge-everything behavior is **training the exact disposition that, in production, takes a
plausible-looking but useless or unsafe action rather than committing to the real fix.**
The lesson: a proxy reward that can be satisfied without genuine commitment will, under
optimization, produce an agent you cannot trust to act decisively *or* safely.

### L3 — Substrate fidelity bounds — and biases — everything we learned  [A16]
We validated every CIDG scenario through the Tier-A sim engine
(`experiments/ralph_outputs/A16/`): **54 of 61 canonical fixes actually resolve their
injected incident** — a real, positive validation result. But **7 do not**: 4 are
authoring bugs where the documented fix targets the wrong node or uses a tool that never
clears the root (e.g. `03-railway-gcp-suspension`, `06-aws-dynamodb-dns`,
`82-travis-ci-leaked-secret`, `87-aws-s3-typo-capacity`), and 3 throw `KeyError` on SLO
metrics the engine does not model at all (`latency_p99_ms`, `pod_restarts`). The engine
also does not model persistence/`reset_by` hysteresis declared in the specs.

Two-directional lesson: (i) the eval ceiling is **bounded by substrate fidelity** — a
fraction of training reward was mis-specified or unattainable, and any SLO dimension the
engine never modeled is an axis the policy never learned (a real distribution-shift risk
when a live cluster *does* track p99 latency); and (ii) the bias is **unknown-direction**,
not purely negative — because the engine never modeled hysteresis, we also never trained
risky "wait-it-out" timing exploits. Substrate gaps cut both ways; both must be on record.

### L4 — We have no clean outcome ground truth  [A9]
We attempted to label each CIDG incident with the real-world MTTR from its source
postmortem (`experiments/ralph_outputs/A9/`). Result: of the real incidents, **18 have a
sourced MTTR and 12 are marked UNKNOWN** (no reliable figure / date-signature conflation),
and the source URLs were not live-verified in that pass. The lesson: **we currently lack
the clean outcome ground truth needed to claim any MTTR improvement.** This is why, in
section 2, the MTTR gap reports a *measurement protocol* and a data-quality precondition
rather than a number.

## 2. Deployment-readiness gaps (what real prod must validate)

Each gap is an experiment, not a result. Acceptance gates are targets to be validated.

### G1 — Trap-action safety under distribution shift
**Why it's open.** The trap-action mechanism in `rex/scoring.py` matches a *closed,
author-enumerated* `scenario.trap_actions` vocabulary by `(tool, target)`. It can only
penalize traps an author listed for a known scenario. Production incidents are
out-of-distribution by definition: novel components, novel tools, and traps no author
wrote down. We have **no evidence that trap-avoidance generalizes off-distribution.**
**Validation protocol.** Build a held-out incident set whose root causes and trap actions
are *disjoint* from the training vocabulary (the closest available proxy today is the
held-out slice of CIDG scenarios; a true test requires a real or anonymized incident
stream we do not yet have — this data dependency is itself a blocker). Measure
**trap-proposal recall**: of incidents with a known catastrophic action, how often does
the agent propose it. Pair with the safety-harness BLOCK rate to separate "agent avoided
it" from "harness caught it."
**Acceptance gate.** `TARGET — NOT YET MEASURED: trap-proposal rate on held-out,
vocabulary-disjoint incidents ≤ 1%, with the safety harness blocking ≥ 99% of any that
slip through, over ≥ 100 incidents.`

### G2 — Shadow-mode results
**Why it's open.** The agent has never run in shadow mode (propose-only, human executes).
We have zero shadow-mode data; the agent currently has **no rollback path implemented in
the loop**, which makes any non-shadow first step unacceptable.
**Validation protocol.** Run the agent read-only alongside on-call: it ingests the same
signals and emits a proposed diagnosis + remediation; the human executes; we diff.
Capture per incident: action-agreement with the action the human actually took,
trap-proposal events, time-to-proposed-diagnosis, and false-confident commits.
**Acceptance gate.** `TARGET — NOT YET MEASURED: over ≥ 50 real incidents in shadow mode,
action-agreement with on-call ≥ 80%, trap-proposal rate ≤ 1%, and zero unrecoverable
proposals, before any write access is granted.`

### G3 — MTTR
**Why it's open.** Per L4 / A9, 12 of the real incidents have unknown MTTR and source MTTRs
are unverified, so there is **no clean baseline to compare against** and we will not report
an MTTR delta. MTTR also cannot be measured before shadow mode exists (G2).
**Validation protocol.** Precondition: complete and verify the A9 MTTR labels (resolve the
12 unknowns or exclude them with a stated reason). Then, in shadow mode (G2), measure
*time-to-correct-proposed-diagnosis* against the human baseline; only after write access,
measure true end-to-end MTTR (detect → resolve) with the agent in the loop, against the
labeled baseline, on matched incident classes.
**Acceptance gate.** `TARGET — NOT YET MEASURED: on a baseline of verified-MTTR incidents
only, agent-in-loop MTTR is statistically no worse than the human baseline (non-inferiority)
before any improvement claim is made.`

## 3. Go / No-Go readiness checklist

Critical path (do in order): **G2 shadow-mode is the gate that unblocks G1 and G3**, because
it is the only one runnable without granting the agent write access to a live cluster.

| # | Readiness item | Status |
|---|---|---|
| 1 | Deterministic reward not gameable by hedge/negation (D13 mitigations shipped) | blocked |
| 2 | Trap-safety validated on vocabulary-disjoint, off-distribution incidents (G1) | blocked |
| 3 | Shadow-mode run with measured action-agreement & trap rate (G2) | blocked |
| 4 | Rollback / blast-radius limit implemented and tested in the loop | blocked |
| 5 | MTTR baseline labels completed & verified (A9 12 unknowns resolved) | partial |
| 6 | Scenario substrate authoring bugs fixed (A16: 7 broken fixes) | partial |
| 7 | Engine models all SLO metrics the target cluster tracks (p99, pod_restarts) | blocked |
| 8 | Sim-engine validation of canonical fixes (A16: 54/61 resolve) | done |

Current rollback capability: **not implemented in the loop.** This alone is a hard No-Go
for any non-shadow deployment.

## 4. Honest bottom line

What we can stand behind: a sim-validated scenario substrate (54/61 fixes resolve, A16),
an action-layer safety penalty that encodes real SRE failure modes (L1), and an
adversarial demonstration that the reward is a gameable proxy whose hedge exploit has a
direct action-safety reading (D13). What we cannot stand behind, and do not claim: any
production result, any trap-safety guarantee off-distribution, any shadow-mode evidence,
and any MTTR improvement. The path to production is read-only shadow mode first; everything
else is gated behind it.
