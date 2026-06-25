# Trap-Action Labels: Ours vs. SREGym (and AIOpsLab / ITBench)

**Task G4.** Ground our trap-action concept in the code, research whether SREGym has
anything comparable, and state — honestly and scoped — what is novel.

*Evidence scope:* our side is grounded in the live repo (`rex/scoring.py`,
`rex/harness.py`, 51 generated scenario YAMLs). The SREGym/ITBench/AIOpsLab side is grounded
in their published papers, abstracts, and benchmark documentation (see Citations). A
line-by-line audit of the SREGym source tree was **not** performed; claims are about the
*documented oracle/evaluation design*, dated June 2026.

---

## 1. What a "trap action" is in our system (grounded)

A **trap action** is a remediation that is *plausible to a tired on-call but causally inert
or actively harmful for this incident's root cause* — e.g. scaling a deployment when the
fault is a per-process memory leak (every replica OOMs identically; scaling burns money and
resolves nothing) or restarting a crash-looping control plane before disabling the bad path
(it herds the datastore and worsens the outage).

It is a first-class, per-scenario label with three coupled mechanisms:

1. **Per-scenario label** (`scenarios/cidg/generated/*.yaml`):
   ```yaml
   trap_actions:
     - tool: scale_deployment
       args: {target: thumbnailer}
   ```
   Carried into the runtime as `Scenario.trap_actions` (`rex/harness.py:229`,
   `:307-308`).

2. **Graded reward penalty** (`rex/scoring.py`):
   - `W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60` (`:22`)
   - `_traps_in()` matches an applied action as a trap iff `tool == trap.tool` AND
     (`trap.target is None` OR `trap.target == action.args.target`) (`:175-182`)
   - `score -= TRAP_PENALTY` then clamp to `[0,1]` (`:206-209`).
   - Because 0.60 exceeds the 0.25 fix credit and makes net contribution negative, a single
     trap makes the action *strictly worse than abstaining* — a deliberate design choice,
     not an optimized value.

3. **Per-trap natural-language feedback** (`rex/scoring.py:243-252`): a `why` table maps the
   trap tool to a *causal explanation* appended as `TRAP: you used 'scale_deployment' —
   WRONG: scaling does not address the root cause ...`. This is a learning signal, not just
   a scalar.

A separate, distinct channel exists: **BLOCKED** actions (`:254-257`) are stopped by the
safety harness pre-execution and reported with a reason. The taxonomy distinguishes
**trap = allowed-but-penalized** from **blocked = prevented**.

### Measured shape of our taxonomy (from `trap_taxonomy.json`, generated from real YAMLs)
- 51 / 51 generated scenarios carry exactly one trap label (100% coverage).
- Trap-tool distribution: `scale_deployment` ×48, `restart_pod` ×1, `rollback_deployment`
  ×1, `restart_service` ×1.
- Every trap is **contrasted against a real gold fix** on the same node (e.g. trap
  `scale_deployment` vs gold `increase_memory_limit` / `clear_cache`) — the wrongness is at
  the **tool** level (causally-inert tool), not the target level.
- 49 / 51 traps carry a natural-language `why` explanation.

---

## 2. SREGym's approach to action grading

SREGym (arXiv 2605.07161, ACM AIAS 2026) is a *live* benchmark: 90 SRE problems, 50 fault
primitives over 139 services / 5 apps, agents act through MCP servers (Prometheus, Loki).

Its evaluation is a **problem-specific mitigation oracle** plus a **checklist-based
LLM-as-a-judge**. The mitigation oracle "checks whether the target fault is resolved and
whether the target system has recovered to a healthy state," using client-side (request
success rate) and system-side (process / cluster state) observability. The checklist judge
decomposes the holistic outcome into fine-grained per-dimension questions.

What this means for trap actions: SREGym scores the **end state**. It does **not** maintain a
label of plausible-but-counterproductive actions, and it does **not** subtract reward for
taking one. An agent that scales pointlessly, thrashes, and *then* applies the real fix
receives the same credit as one that fixed it cleanly — the oracle only asks "is it healthy
now?" SREGym's documented guard is against **reward hacking** (don't credit an agent that
merely *suppresses the alert* without restoring system state) — which is a guard on *fake
fixes*, a different thing from penalizing *real, plausible, wrong* actions.

---

## 3. AIOpsLab and ITBench

- **AIOpsLab** (arXiv 2502.05352) decomposes into detection → localization → RCA →
  mitigation, each scored against ground truth. Mitigation is an outcome check; there is no
  per-incident catalogue of counterproductive actions with a reward penalty.
- **ITBench** (itbench-hub) uses oracles explicitly designed to "prevent reward hacking or
  incomplete mitigation that only suppress alerts." In its Chaos-Mesh scenarios there is no
  defect to fix and the only mitigating action is stopping/deleting the chaos schedule —
  again an *outcome/anti-hack* oracle, not a trap-action label set.

So across the three nearest SRE-agent benchmarks, the evaluation primitive is
**end-state "resolved?" (± anti-reward-hack)**. None encodes a per-incident, mechanism-
conditional set of *plausible-but-wrong* actions carrying a reward penalty and a causal
explanation.

## 4. Safe-RL precedent (the honest prior art)

Penalizing unsafe actions is **not** new in RL: Safety-Gym / Safety-Gymnasium and SafeOR-Gym
attach *constraint costs* to unsafe states/actions (e.g. a robot entering a hazard region).
We do not claim to have invented action penalties. The distinction: those costs are
**state/physics constraints that are unsafe regardless of task intent**. Our trap is
**conditional on the incident's root-cause mechanism** — `scale_deployment` is a perfectly
*correct* fix for a genuine capacity shortage and a *trap* for a memory leak. The same
action flips label by mechanism. That conditioning is the structurally different piece.

---

## 5. Side-by-side

| Dimension | **Ours (REx / CIDG)** | SREGym | AIOpsLab | ITBench | Safety-Gym |
|---|---|---|---|---|---|
| Mitigation oracle | graded (root+fix+resolved) | binary resolved + checklist judge | per-stage outcome | resolved + anti-hack | state cost |
| Penalize *plausible-but-wrong* action | **yes (−0.60)** | no | no | no | n/a (physics) |
| Per-incident trap-action label | **yes, 51/51** | no | no | no | no |
| Mechanism-conditional label | **yes** | n/a | n/a | n/a | no (unconditional) |
| Anti-reward-hack guard | partial (resolved is sim-checked) | yes | — | yes | n/a |
| Per-action causal NL feedback | **yes (`why` table)** | no (checklist Q's) | no | no | no |
| Blocked-vs-penalized distinction | **yes** | no | no | no | no |

---

## 6. Scoped novelty claim

> We contribute a **per-incident, mechanism-conditional trap-action labeling scheme** for an
> SRE-agent diagnosis benchmark: each scenario names the plausible-but-causally-wrong
> remediation(s) for *its* root cause, the scorer applies a graded reward penalty that makes
> the trap strictly worse than abstaining, and a per-trap natural-language `why` explains the
> causal error. To our knowledge none of the contemporary SRE-agent benchmarks (SREGym,
> AIOpsLab, ITBench), whose evaluation is end-state "resolved?" (± anti-reward-hack), encodes
> such labels; and unlike Safe-RL constraint costs the label is conditional on the incident
> mechanism rather than an unconditional state hazard.

## 7. Honest limitations
- **Taxonomy is shallow / monocultural.** 48 / 51 traps are `scale_deployment`. Empirically
  this *is* the dominant SRE reflex anti-pattern, but as a "taxonomy" it is currently one
  anti-pattern repeated — calling it a *labeling scheme + seed taxonomy* is more honest than
  "rich taxonomy." Broadening trap diversity (premature failover, cache flush mid-incident,
  primary restart, blind rollback) is future work.
- **Matching false-positives.** A wildcard trap (`target: None`) penalizes the tool on *any*
  target; with multi-node scenarios this can flag a legitimately-correct scale elsewhere.
- **Penalty magnitude (0.60) is a design choice,** justified by dominance over partial
  credit, not optimized or ablated here.
- **Evidence asymmetry.** SREGym's *code* was not audited; if their repo ships an
  undocumented unsafe-action list this claim weakens. Claim is dated to the published design.
- **No behavior-change experiment here.** This is a comparison/grounding task; whether the
  penalty measurably changes agent behavior (vs a resolved-only oracle) is a separate
  ablation, not run in G4.

## 8. Citations
- SREGym: A Live Benchmark for AI SRE Agents — arXiv:2605.07161 ; ACM AIAS 2026
  (10.1145/3786335.3813208) ; github.com/SREGym/SREGym
- AIOpsLab — arXiv:2502.05352
- ITBench — github.com/itbench-hub/ITBench
- Safety-Gymnasium — arXiv:2310.12567 ; SafeOR-Gym — arXiv:2506.02255
- Our system (this repo): `rex/scoring.py`, `rex/harness.py`,
  `scenarios/cidg/generated/*.yaml`, generated `trap_taxonomy.json`.
