# E6 — 02 Grill (5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial takes

**SMR:** An ablation over supervision channels is the right scientific frame. But
"state-only vs action-only" must be a *clean partition* of the trajectory, or the
ablation conflates information with quantity. Define exactly what bytes each variant
keeps and prove the union reconstructs `full`.

**PSRE:** From an ops view the channels are not symmetric. A state-only stream
(metrics moving, pods restarting) is what an on-call SRE actually sees on a dashboard
*before* anyone acts. Action-only (a runbook of commands with no telemetry) is what a
junior copies blindly. The ablation literally tests "dashboard-watcher vs runbook-parrot."
That's a great story — but action-only must keep the *canonical fix*, else it's empty.

**AAAI:** Where are the numbers? An ablation with no train/eval is not a result. If you
can't run the model, say so loudly and don't dress up a data-munging script as science.
I will reject any table that looks like fabricated pass@1.

**RLE:** For RL/SFT, the variant that matters is whether the *reward-bearing* signal
survives. state_before/state_after IS the reward proxy (recovery_check). If action_only
drops state_after, you can't compute reward for it — that's fine for SFT but means
action_only is un-RL-able. Call that out.

**DOL:** Operationally, just make it a deterministic transform with a fixture so it runs
in CI without a cluster. Don't touch shared core. One CLI, one report.

## Round 2 — react to another persona (genuine disagreement)

**AAAI → PSRE:** I disagree with PSRE's tidy "dashboard vs runbook" narrative. It
over-claims. state-only is NOT what an SRE sees — it's tool *results with the agent's
reasoning stripped*, which no human or model normally consumes. The framing is a
post-hoc just-so story. Keep it as a hypothesis, not a finding.

**PSRE → AAAI:** Pushing back — AAAI is being purist. The narrative is a *motivation*,
not a claimed result. Motivation doesn't need a p-value. The transform is still the real,
falsifiable artifact; the story explains *why we'd bother*.

**RLE → SMR:** SMR wants a perfect partition, but I disagree that the partition should be
total. `remediation.canonical_fix` is an action artifact that BOTH humans would want, yet
SMR's "union == full" rule forces it into exactly one bucket. I'd duplicate the fix into
action_only and the state numbers into state_only — overlap is acceptable when a field is
genuinely dual-channel. Strict partition is elegant but wrong for the remediation block.

**SMR → RLE:** Conceding partially. The *trajectory steps* must partition strictly (an
assistant step is an action, a tool step is a state — no overlap, provable by count). But
the *remediation block* is a separate dict and I accept RLE's key-level split there:
state keys to state_only, action keys to action_only. So: strict partition on steps,
key-partition on remediation. That's defensible and testable.

**DOL → AAAI:** AAAI's "no numbers = no value" is too harsh for a blocked task. The brief
explicitly says a correct scaffold + honest blocker beats fabricated numbers. A tested,
schema-correct transform that runs on 319 real records IS a shippable deliverable.

## Round 3 — synthesis

Consensus:
1. **Trajectory steps partition strictly**: assistant→action_only, tool→state_only.
   Test asserts `len(state_only) + len(action_only) == len(full)`. (SMR, RLE)
2. **Remediation splits by key**: `state_before/after, recovery_check, primary_metric,
   direction, resolved` → state_only; `fix_tool, canonical_fix, trust_tier` → action_only.
   Overlap is allowed only at the remediation level and is intentional. (RLE, SMR)
3. **No fabricated metrics.** Harness emits structural stats only; train/eval blocker
   documented prominently. (AAAI, DOL)
4. **RL caveat**: action_only has no state_after → no computable reward → SFT-only.
   Document it. (RLE)
5. **Narrative is motivation, not result.** "dashboard vs runbook" framed as hypothesis. (PSRE/AAAI truce)
6. **CI-runnable**: deterministic, fixture-backed, stdlib + pytest, no shared-core edits. (DOL)
