# A15 — Grill (5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (AAAI)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes
- **SMR:** Good — a "noisy metrics" variant is a *distribution shift* on the observation
  channel only. As long as the reward/ground-truth (`is_resolved`) is unchanged, this is a
  clean controlled axis: same task, harder perception. That's exactly the kind of paired
  variant you want for an ablation.
- **PSRE:** Realistic. In a real Sev1 the alert console is a wall of red and the one useful
  log line is buried under hundreds. Burying the smoking gun deeper and flipping
  `monitoring_degrades` captures "you can't trust your dashboards." Good.
- **AAAI:** I want to know the *mechanism*. Does the engine actually act on `alerting=noisy`
  and `monitoring_degrades`, or are these inert metadata? If the Tier-A engine ignores them,
  the "variant" changes nothing the agent experiences and the claim is hollow.
- **RLE:** If these fields don't perturb the observation the agent sees, then for the frozen-LLM
  harness this is a no-op and we'd be shipping a placeholder. Need to be honest about that.
- **DOL:** Operationally fine, but make sure I can regenerate the variant for *any* baseline with
  one command and that it never clobbers the source-of-truth scenarios. Reproducibility > a hand-edited YAML.

## Round 2 — genuine disagreement (react by name)
- **RLE → AAAI (disagree):** You're conflating "the spec field is inert in *today's* Tier-A
  `propagate()`" with "the variant is hollow." The spec is the *single source of truth* for both
  the fast sim AND the live mesh + the observation tool layer (smoking guns are read by
  `get_logs`/`query_traces` with `buried_under` noise). `buried_under` is consumed where the
  agent reads logs, not in `propagate()`. So burying the gun deeper IS a real perception change
  even if error_rate math is untouched.
- **AAAI → RLE (push back):** Then *prove the consumption path* or scope the claim. If A15's
  deliverable is only the spec transform, the honest framing is: "this produces a
  schema-valid variant that the observation layer is *designed* to consume; wiring the
  engine to amplify alert noise from `alerting=noisy` is downstream work." Don't claim a
  behavioral effect you didn't measure.
- **PSRE → SMR (disagree):** You called it "perception only / physics unchanged" — but I'd argue
  adding a `monitoring` node into the blast radius is *not* purely cosmetic: under the schema,
  an `observes` edge into a degraded region is what *causes* monitoring to degrade. That's a
  small topology change. SMR is right that reward is unchanged, but "zero physics change" is too strong.
- **SMR → PSRE (concede partially):** Fair. The reward/ground-truth (`root_cleared && slo_ok`) is
  unchanged, which is what matters for the controlled comparison. I'll restate as "reward-invariant,
  observation-degraded" rather than "physics-identical," and only add the monitoring node when the
  baseline lacks an observes edge.
- **DOL → AAAI:** Agree with you on scoping the claim, disagree on "hollow." A correct, validated,
  one-command transform that other tasks can run on all 33 scenarios has standalone value as
  research infrastructure even before the engine consumes every field.

## Round 3 — synthesis
Consensus:
1. Frame the variant as **reward-invariant, observation-degraded** (not "physics-identical").
2. Be explicit and honest: `buried_under`/`alerting` are consumed by the *observation/tool
   layer* and the live mesh, not by Tier-A `propagate()` today; do NOT claim a measured
   behavioral delta. Document this as a scoped blocker in `07`/`09`.
3. Only inject the monitoring node + observes edge when needed for schema validity, and keep
   root_cause/canonical_fix byte-identical so the comparison is clean.
4. Ship it as a **reusable transform + tests**, not a hand-edited YAML — DOL's reproducibility point.
