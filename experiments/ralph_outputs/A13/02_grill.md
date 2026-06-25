# A13 — Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**AAAI** (AAAI Reviewer), **RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial take

**SMR**: Multi-fault is the right axis of difficulty. Single-fault tasks reward greedy
symptom-chasing; the agent learns "find loudest alert → apply the one matching tool → done."
Two simultaneous faults break that policy because resolving requires the agent to NOT stop after
the first fix. But I worry the reward signal must be *conjunctive* (both cleared) or it teaches
nothing new.

**PSRE**: From real ops, "two simultaneous faults" is usually one of two shapes: (a) **independent
coincidence** — a cert expires while, unrelated, a connection pool leaks; or (b) **masking** — fault
A's symptoms hide fault B until A is fixed. Shape (b) is far more valuable for training because it
defeats parallel diagnosis. The YAMLs should make at least one a masking pair.

**AAAI**: My concern is *construct validity*. If the underlying simulator injects only one fault,
then a "2-fault" YAML is a label, not a mechanism. A reviewer will ask: does the environment
actually instantiate two faults, and does the metric `is_resolved` require both to clear? If not,
this is a paper-thin contribution. Show the mechanism or don't claim it.

**RLE**: I care about the action budget and credit assignment. Two faults means the optimal
trajectory is strictly longer (≥2 remediations + the diagnosis between them). If `pass@k` is the
metric, k may need to rise. Also: are the two fixes *order-independent*? If not, you've smuggled in
an ordering task too — fine, but declare it.

**DOL**: Practical: don't break the existing 33 specs or the registry. New files, unused numbers,
must still `validate`. And the `tools_registry.json` action space is fixed — both fixes must use
tools already in it. No new tools.

## Round 2 — react to another persona (genuine disagreement)

**AAAI → SMR**: I disagree with SMR's framing that "the right reward is conjunctive and that's
enough." Conjunctive reward over a sim that only injects ONE fault is *vacuously* satisfiable —
clearing the single injected node trips `root_cleared` and the SLO recovers, so the agent gets full
reward having touched only one fault. The label says 2, the physics says 1. That's not a hard task;
it's a mislabeled easy one. SMR is reasoning about the reward as if the mechanism already exists. It
does not in the unpatched engine.

**SMR → AAAI**: Partially conceding, but AAAI overstates. The contribution can be the *mechanism
design* + *valid data*, with the engine change delivered as a patch, **provided** the data is
authored so that once the patch lands it is immediately correct — i.e. two distinct clearable
locations, two SLO victims, two canonical-fix steps. If I author it sloppily (second fault on a node
with no SLO, no fix tool) then AAAI is 100% right and it's decorative forever. So the burden is on
*data faithfulness*, not on shipping an engine edit we're forbidden to make.

**PSRE → RLE**: I push back on RLE's "make them order-independent for simplicity." In production the
nastiest multi-faults are order-*dependent* — you cannot drain the pool leak until you've renewed
the cert that's causing the retry storm refilling the pool. Sanding that off makes the task
unrealistic. At least one of the three specs should be order-coupled via an edge so the engine's
cascade actually enforces it. Independence is the boring case.

**RLE → PSRE**: Disagree on scope. Order-dependence + 2 faults + masking in one spec is three new
difficulty axes at once; you can't attribute a failure to any one of them in an ablation. Keep the
*first* multi-fault specs clean: 2 independent faults, both with SLOs and fixes, order-free. Add a
coupled one as a deliberately-labeled third spec so analysis can separate the effects. PSRE is
optimizing realism at the cost of measurability.

**DOL → AAAI**: Agree with AAAI's mechanism worry but on *my* terms: even decorative-today YAMLs are
useful IF they parse, validate, and don't corrupt the registry — they become live the moment the
patch merges. The failure mode I won't accept is a YAML that silently *fails to validate* and rots.
So whatever extra block we add for the 2nd fault MUST survive `sim.spec.load_spec` + `validate`
with zero errors today. (It does: `_build` drops unknown keys.)

## Round 3 — synthesis

Consensus reached:
1. **Author 3 specs**, not 1, to separate difficulty axes (RLE + PSRE compromise):
   - `80` independent coincidence (cert_expire + pool_leak), order-free, the clean baseline.
   - `81` masking (bad_revision masks cache_flush), order-free but diagnostically coupled.
   - `82` resource coupling (fd_exhaust + cpu_starve sharing a victim), the harder case.
2. **Data faithfulness is the real deliverable** (AAAI + SMR): each spec declares 2 distinct fault
   locations, each with its own SLO victim and its own canonical-fix step using existing tools.
3. **Engine injects one today**; ship `engine_multifault.patch` documenting the conjunctive-clear
   extension so the claim is mechanistic, not cosmetic (AAAI). Do NOT apply it (no-edit rule).
4. **Validate + test today** (DOL): all 3 parse, validate clean, primary path runs in unpatched
   engine; test asserts 2 distinct fault locations + SLO victims per spec.
5. **No new tools** (DOL): every fix uses `tools_registry.json` entries.
