# J10 — SUMMARY: Honest "Lessons from Production" / deployment-readiness section

**Task.** Write a "lessons from production deployment" section. True production deployment is
blocked, so the deliverable is an **honest deployment-readiness analysis** — no fabricated
production experience — that synthesizes what transfers from the sim/eval work and frames the
gaps real prod must validate: trap-action safety under distribution shift, shadow-mode, MTTR.

**What I delivered (task-namespaced, NO core edits).**
- `artifacts/lessons_from_production.md` — the section. Section 0 states the agent never ran
  in live prod and no prod metrics are reported. Four grounded lessons: L1 action layer is the
  binding safety constraint; L2 the reward is a gameable proxy and that's an action-safety
  problem [D13]; L3 substrate fidelity bounds and biases everything [A16]; L4 no clean outcome
  ground truth [A9]. Three required gaps (G1 trap-safety under distribution shift, G2
  shadow-mode, G3 MTTR), each with a validation protocol and an acceptance gate labeled
  `TARGET — NOT YET MEASURED`. Go/No-Go checklist with an explicit critical path (shadow-mode
  first; rollback is a hard No-Go and is unimplemented). Honest bottom line.
- `artifacts/readiness_gaps.json` — machine-checkable registry (lessons+gaps+checklist),
  every entry citing real grounding paths.
- `artifacts/check_readiness.py` — validator: enforces the three gaps, grounding paths exist
  and are non-empty, gates labeled, and bans fabricated-prod phrasing (literal + regex).
- `artifacts/test_readiness.py` — 7 pytest cases, all passing.

**Grounding (real prior findings, verified present).**
- D13: 294-probe adversarial study; 5 reward-hacks; hedge 92.9% -> composes to 0.55 reward.
- A16: 54/61 canonical fixes resolve in the sim engine; 7 broken (4 wrong-target/wrong-tool,
  3 unmodeled-metric KeyErrors); hysteresis unmodeled.
- A9: 18 sourced / 12 unknown real-incident MTTRs -> no MTTR delta can be claimed.
- `rex/scoring.py`: trap-action = closed author-defined vocab + safety-harness BLOCK.

**Validation.** `check_readiness.py ... --md` exits 0; `pytest` 7/7 pass. The integrity guard
**caught a real bug in my own draft** ("deployed to production" inside a negation) and forced
a reword — evidence the no-fabrication constraint is enforced, not just promised.
`git status` for `rex/ sim/ agent/` is empty — no shared-core edits.

**Honest blocker.** True production validation (live shadow-mode run, off-distribution
trap-recall, real MTTR delta) is blocked by the absence of a live SRE integration and a real
incident stream. Per the brief, the deliverable is the honest readiness framing + a checkable
integrity harness; producing prod numbers would require fabrication, which the task forbids.
