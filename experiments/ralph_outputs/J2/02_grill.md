# 02 — Grill (5 personas, 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial takes
- **PSRE:** Shadow mode is the only ethically deployable first step against prod. But
  "the agent doesn't write" is necessary, not sufficient — does the *observation* path
  read-only? A naive scrape that hits a service's `GET /` actually drives load and, in
  this mesh, mutates request counters. Read the dedicated `/metrics`, never `/`.
- **SMR:** The interesting research artifact is the *diagnosis*, not the non-action.
  Log the agent's stated root cause vs the known fault so we can later score shadow
  accuracy offline. Otherwise this is just a plumbing exercise.
- **REV:** Claiming a "safety guarantee" demands more than a flag check. A reviewer
  wants the guarantee to be *structural* — show the execution code path literally cannot
  be reached. A boolean `if shadow: return` is one refactor away from a prod incident.
- **RLE:** If you reuse `rex.loop.propose`, you're coupling to a live LLM key. That's a
  second hidden dependency. Make the proposer injectable so the harness is testable
  without a model, and so the safety property is provable in CI.
- **DOL:** Where does telemetry come from when there's no cluster? If the answer is
  "we mock it," say so loudly and keep the live path identical, or you'll ship a harness
  that's never actually touched real Prometheus shape.

## Round 2 — react to another persona (genuine disagreement)
- **REV → SMR:** I disagree that diagnosis is the point. For a *safety* deliverable, the
  load-bearing claim is non-execution. A great diagnosis with a hidden write path is a
  failure; a mediocre diagnosis that provably writes nothing is the actual deliverable.
  Prioritize the guarantee; diagnosis logging is secondary.
- **SMR → REV:** Pushing back — a non-action with no diagnosis is worthless. Nobody
  ships shadow mode forever; it exists to *build trust toward acting*. With no diagnosis
  record you can never graduate it. Both matter, but a guarantee protecting an empty
  observation is theater.
- **PSRE → DOL:** Disagree that mocking is fine "if loud." A fixture that doesn't match
  real Prometheus exposition shape is worse than nothing — it hides the parser bug you'll
  hit on day one. The fixture must be a *recorded real* `/metrics` snapshot, exact format.
- **RLE → PSRE:** Half-agree. Real shape matters, but you can't gate the whole harness on
  a live cluster nobody here can reach. Recorded-real fixture is the compromise: real
  bytes, offline. The live path stays identical; only the byte source differs.
- **DOL → RLE:** Injectable proposer is right but don't over-abstract. One function
  `propose_fn(observation)->plan` is enough; a plugin registry is yak-shaving for a
  vertical slice.

## Round 3 — synthesis
Consensus the team will hold to:
1. **Guarantee is structural** (REV wins the framing): no `apply_action`, no `subprocess`/
   `kubectl`, no `/ctl` POST in the module; a test greps for their absence; `executed_count`
   is asserted 0 and a violation raises.
2. **Observation is strictly read-only** (PSRE): scrape `/metrics`, never `/`.
3. **Diagnosis IS logged** (SMR): `stated_root_cause` + derived cascade victims in the
   report, so shadow accuracy is scoreable later.
4. **Proposer is injectable** (RLE/DOL): testable offline; live-LLM path optional.
5. **Recorded-real fixture** (PSRE/DOL): exact Prometheus shape, faulted mesh, offline.
6. Keep it a vertical slice — no plugin registry (DOL).
