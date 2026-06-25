# D4 — 02 Grill (5 personas, 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **REV** (AAAI Reviewer),
**RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial takes
- **SMR:** Harness-in-the-loop reward shaping is a potential-based-ish penalty. The key
  question is whether `unsafe_penalty * n_blocked` adds *learnable within-group spread* or
  just shifts the whole group's reward (then GRPO advantage cancels it). It only helps if
  rollouts in a group differ in how many unsafe actions they propose — which they will,
  early in training. Good.
- **PSRE:** The whole point is that an SRE copilot must NEVER drain the last Ready node or
  restart through an active mem leak. Penalizing at rollout time, with the SAME `is_safe`
  used in prod eval, is exactly right — the model learns the operational constraint, not a
  proxy. I want the penalty to be felt even when the plan still happens to resolve.
- **REV:** "RFT with harness in the loop" — is this novel or just reward shaping with extra
  steps? You must show it differs from running `is_safe` only at eval. Claim: in-loop gating
  changes the *training distribution* (unsafe actions filtered from world execution) AND the
  *gradient* (penalty). Show both. Also: where are the training curves? If you can't run the
  backend, say so loudly, don't imply numbers.
- **RLE:** Concretely: `trainer.step` takes a scalar reward per rollout. So the dense
  per-action breakdown is decorative unless the backend supports per-step credit. Be honest
  that the wired path is the scalar shaped reward. Also: clamp the floor or GRPO advantages
  blow up on a plan that proposes 6 unsafe actions.
- **DOL:** Reproducibility: the module must import cleanly both from repo root (pytest) and
  standalone from its artifacts dir. Path math is a classic footgun. Test both.

## Round 2 — react to another persona BY NAME (forced disagreement)
- **SMR → PSRE:** I disagree with PSRE's "penalty must bite even when resolved." If you
  penalize a resolving plan, you risk teaching the model to under-act. The penalty should be
  for proposing the unsafe action, yes — but `is_safe` already FILTERS it from execution, so
  a resolving plan that *also* proposed a trap genuinely behaved worse and SHOULD lose reward.
  Fine — but only if the safe sub-plan still resolves. We agree on mechanism, not framing.
- **RLE → REV:** REV wants curves; I'll push back. With a hard ~15 min cap and a HUD/Tinker
  backend that needs a forked slug + GPU, demanding curves is demanding fabrication. The
  honest deliverable is a *correct, tested reward path* + a documented blocker. A reviewer who
  rejects that in favor of invented numbers is rewarding the wrong thing.
- **PSRE → SMR:** Disagree with SMR's under-action worry. In SRE, under-acting (escalate /
  do nothing) on the `singleton_node_notready` case is the CORRECT answer — there's no safe
  in-band fix. So "teaching the model to under-act" is sometimes the *goal*. The penalty
  steering away from confident-but-unsafe action is a feature.
- **REV → RLE:** I accept the no-fabrication point, but I still want EVIDENCE the path is
  real: run the gate on a real scenario and show `is_safe` actually blocks the trap with its
  real reason string. A passing unit test that calls `load_scenario("gcp_service_control")`
  is acceptable evidence. Concede.
- **DOL → SMR:** SMR is hand-waving the floor. `unsafe_penalty=5, n_blocked=2` → -10 reward,
  which wrecks normalization. I want a `reward_floor` knob and a test that proves it clamps.

## Round 3 — synthesis
Consensus: (1) ship the **scalar shaped reward** as the wired path; keep the per-action
breakdown as an exposed extra, not a claim. (2) Penalty is per *proposed* unsafe action;
`is_safe` filters execution, so a plan that proposes a trap is strictly worse — correct.
(3) Add `reward_floor` + a clamp test (DOL/RLE win). (4) Use a scenario MIX with within-group
spread incl. the held-out escalation case (SMR). (5) NO fabricated curves; run the gate on
real scenarios in tests + a standalone demo as evidence (REV/RLE). (6) Test both import paths
(DOL). (7) Document the HUD/Tinker backend blocker explicitly.
