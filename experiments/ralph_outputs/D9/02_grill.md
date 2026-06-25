# D9 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI
Reviewer · **RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial takes
- **SMR:** Curriculum learning is well-trodden (Bengio 2009). The clean part of
  this task is that A12 gives a *static-structural* difficulty signal — no
  rollouts needed to order, so the curriculum is reproducible and cheap. The
  risk is that static difficulty ≠ learning difficulty; a graph can be "big" but
  trivially diagnosable.
- **PSRE:** From an incident-response lens, "easy→hard" should mean single-leaf
  faults first (loud alert = cause), cascades and hysteresis traps last. A12's
  order does exactly that (sidecar cert-expire easiest, FD-exhaustion cascade
  hardest). I buy the ordering operationally.
- **AAAI:** Where is the *baseline*? A curriculum claim is meaningless without a
  random-ordering control and ideally an anti-curriculum control. Also: one seed
  is not a result.
- **RLE:** For GRPO you need within-group reward spread per band. If stage 0 is
  all 0.9-difficulty incidents the model one-shots, the group reward is flat and
  the gradient is ~0. Banding must preserve spread.
- **DVO:** Can this actually run in 15 min with no GPU? If it needs the Tinker
  SDK / a live model, it's blocked. Be honest about that up front, don't fake a
  training curve.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree that static difficulty is "good enough." For RL the
  thing that matters is reward *gradient*, not graph size. Two incidents with
  identical A12 difficulty can have wildly different reward variance under the
  current policy. A static curriculum can stall a learner on a band where every
  sample is already solved (no signal) or already impossible (no signal).
- **SMR → RLE:** Partly fair, but you're letting perfect beat good. Self-paced /
  teacher-student curricula need *online* competence estimates, which need the
  very training loop DVO says is blocked. A static A12 prior is the correct
  *offline* deliverable; the online refinement is future work, not this task.
- **AAAI → DVO:** I push back on "just document the blocker and stop." A blocked
  training run is fine, but then the comparison harness MUST be something other
  than vibes. If you simulate, the simulation has to encode a falsifiable
  mechanism and be labeled as a model, not smuggled in as measured reward.
- **PSRE → AAAI:** Disagree that the random control is the hard part. The hard
  part is that "difficulty" for SRE is multi-dimensional — a tiny topology with
  a buried smoking gun under monitoring-degradation is brutal. A12's weights
  already over-weight the trap booleans (loud_not_cause=2.5, hysteresis=2.0)
  over size (0.6), so the order is trap-first, not size-first. Good.
- **DVO → RLE:** Your within-group-spread concern is real but it's a *config*
  knob, not a blocker — set group_size and let bands span a difficulty range
  rather than a single value. That's cheap to honor in the schedule.

## Round 3 — synthesis
- Static A12 ordering is the right **offline** deliverable; flag online/self-paced
  curriculum as explicit future work (concede RLE's point as a limitation, not a
  redesign).
- Comparison harness must include **random + anti-curriculum controls** and
  **multi-seed** random (concede AAAI).
- Because training is blocked (DVO), the harness runs a **transparent simulation**
  with a documented mechanism (competence-vs-difficulty band), loudly labeled,
  with a one-function seam to swap in real eval (rex.scoring.score_plan).
- Schedule should band a difficulty *range* per stage (not a single value) and
  expose group_size so reward spread is preserved (concede RLE/DVO config point).
- Keep the trap-weighted A12 order as-is (PSRE): it is trap-first, not size-first.
