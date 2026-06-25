# Conclusion

## Graduation, not deployment

The default stance toward an autonomous incident-response agent is **deployment**: run a
benchmark, clear a threshold once, push to production, and trust the system by default
thereafter. We argue for a different stance — **graduation, not deployment**. Where
deployment confers a blanket, standing license on the strength of a single passing score,
graduation confers trust the way a profession does: *scoped to a competence, earned by
demonstrating understanding rather than outcomes, tiered, and revocable.* The distinction is
not rhetorical. It is the organizing principle of SRE-Degrees, and it is encoded in machinery,
not in adjectives. (To be unambiguous for an operations audience: "deployment" here means the
cultural posture "passed once → trusted by default," not a CI/CD push.)

## What makes graduation real

Four mechanisms in the repository turn the metaphor into something mechanical and checkable.

**1. A transcript of tiered, revocable trust.** Every tool in `tools_registry.json` carries a
trust tier — `autonomous` / `approval` / `blocked`. Trust is never global; it is granted
per-capability. The design promotes a tool from `human-approval` → `autonomous` (or demotes
it) based on proven consistency, exactly as a junior engineer earns the pager one service at a
time. A graduate of this program does not receive a key to production; it receives a transcript,
and the transcript can be amended downward.

**2. An exam that cannot be crammed.** The reward in `rex/scoring.py` is
`0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap`. "The metric came back up" — the
thing a deployment gate typically checks — is worth at most 45%. A policy that restarts or
scales until the dashboard turns green but *misdiagnoses the mechanism or trips the trap*
cannot pass: the trap penalty of −0.60 zeroes it out, and diagnosis credit is judged on the
mechanism, not the surface (a config crash diagnosed as "resource exhaustion" earns nothing).
You cannot deploy your way to this credential; you must demonstrate that you understood what
broke. That is the difference between shipping a binary and conferring a degree.

**3. A degree program, not a single test.** `rex/curriculum.py` is a difficulty gradient:
fifteen generated single-leaf incidents where the loud alert *is* the cause, followed by five
reconstructed real-world cascades where the loud alert points at a downstream **victim** and
the naive fix makes things worse. You do not graduate on the easy tier. You graduate by
holding up on the cascades that mislead frontier models on their first attempt.

**4. Escalation as a passing grade.** The signature of a trustworthy graduate is knowing the
limit of one's own competence and handing off — and the environment rewards exactly that. As
`ARCHITECTURE.md` documents, the converged ceiling under refinement is `(4×1.0 + 0.30)/5` =
**0.86**: every model solves the four solvable incidents *and correctly escalates the one
unsolvable incident* (`singleton_node_notready`, which has no safe fix) instead of flailing.
Escalation is not a failure mode here; it is the most professional thing the agent can do.

## The evidence

What persuades us is behavior before arithmetic. On the hard tier, zero-shot models floor at
roughly **0.19–0.42**, with many incidents scoring outright 0.0 — they confidently treat the
victim as the cause and trip the trap. The refinement loop (REx) wrapped around the *same
frozen models* lifts this to **0.59–0.71**, roughly tripling it, and — the most
graduation-shaped fact in the project — **haiku+REx (0.68)** beats raw **opus zero-shot
(0.42)**. Competence is conferred by the program, not innate to the model.

The same shape holds on the curated five-incident suite: baselines spread from 0.63 to 0.81
across five frontier models and four providers, and under REx they *converge to a uniform
0.86*, with the largest lifts going to the weakest baselines (`claude-haiku-4-5`: +0.23). This
compression is the institutional-accreditation story made literal: a single program standardizes
heterogeneous models to one bar. And 0.86 is an *argued* ceiling, not saturation — it is
precisely solve-four-plus-escalate-one, `(4×1.0 + 0.30)/5`. The reward math (mechanism 2) is
what makes that behavior the rational strategy rather than reward-hacking.

## What this degree certifies — and what it does not

A SRE-Degrees credential certifies that, within the environment's scenario distribution, a
frozen policy plus the refinement loop and the safety gate (a) diagnoses the *mechanism* of a
cascade rather than chasing the loudest alert, (b) applies the causal fix without tripping the
known trap, and (c) escalates rather than acting when no safe fix exists. It does **not**
certify production safety in the open world. The cohort is small — five frontier models across
the curated suite, fifteen-plus-five curriculum incidents; the diagnosis grade leans on an
LLM-judge over the mechanism; and the simulation, though emergent rather than scripted, is not
the cluster. Crucially, the demotion arrow of the trust transcript — pulling a tool back from
`autonomous` to `approval` after a regression — is *designed and partially exercised by the
safety gate, but not yet automated as a closed RLHF loop.* A degree is a strong signal, never a
guarantee, and we state its boundaries plainly rather than letting the metaphor overreach.

## Future cohorts

The next program iterations close exactly these gaps: automate the demotion loop so the
transcript updates from observed regressions without a human in the path; widen the curriculum
beyond five real cascades and validate labels with an independent oracle rather than a single
judge; and graduate cohorts on the live cluster, not only the simulator. The thesis stands:
the right way to grant an agent autonomy is to make it **earn a degree through graduated,
mechanism-aware, revocable evaluation** — to graduate it, not to deploy it.
