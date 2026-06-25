# J10 — Plan: "Lessons from Production Deployment" (honest, deployment-readiness framing)

## Objective
Write a **truthful** "Lessons from Production Deployment" section for the SRE-Degrees
write-up. True production deployment of the REx agent is **blocked** (no live SRE
on-call integration, no shadow-mode telemetry, no real-incident MTTR ground truth wired
into the loop). The honest move is therefore to:

1. Synthesize the **real lessons that DO transfer** from the simulation + eval work
   (things we actually learned and can defend), and
2. Explicitly frame the **deployment-readiness gaps** — what would HAVE to be validated
   in real prod before anyone trusts this agent to touch a live cluster: trap-action
   safety under distribution shift, shadow-mode results, MTTR.

Hard constraint from the task: **do NOT fabricate production experience.** No invented
incident counts, no invented MTTR-reduction percentages, no "we ran this on call for 3
weeks." Every claim is either (a) grounded in a real artifact in this repo, or (b)
clearly labeled as an open question / required-future-validation.

## Grounding (real findings I will cite — verified to exist)
- **D13** (`experiments/ralph_outputs/D13/`): adversarial probe over 42 scenarios × 7
  attacks (294 probes) found 5 working reward-hacks of the deterministic diagnosis judge
  in `rex/scoring.py` (negation 100%, single-token 100%, wrong-component 100%, hedge
  92.9% → composes to 0.55 reward, homoglyph 85.7%). **Reward signal is gameable.**
- **A16** (`experiments/ralph_outputs/A16/`): sim-engine validation of CIDG scenarios —
  54/61 canonical fixes resolve; **7 are broken** (4 wrong-target/wrong-tool authoring
  bugs, 3 unmodeled-SLO-metric KeyErrors). **The training substrate has authoring gaps,
  and the engine doesn't model every SLO metric or persistence/hysteresis.**
- **A9** (`experiments/ralph_outputs/A9/`): MTTR labels — 18 real incidents have a
  sourced MTTR, **12 real incidents have UNKNOWN MTTR**, URLs not live-verified.
  **We do not have clean MTTR ground truth, so we cannot claim an MTTR delta.**
- **`rex/scoring.py`**: the trap-action mechanism is a static keyword/target match against
  an **author-defined** `scenario.trap_actions` list, plus a safety harness that BLOCKS
  some actions. This is a closed vocabulary — it only catches traps the author enumerated.

## Approach
Write a single self-contained markdown deliverable (`artifacts/lessons_from_production.md`)
structured as: (1) framing / what "production" means here and why it's blocked;
(2) lessons that transfer (each tied to a real finding); (3) the three named
deployment-readiness gaps (trap-action safety under distribution shift, shadow-mode,
MTTR) each with a concrete validation protocol; (4) a go/no-go readiness checklist.
Add a small **machine-checkable** companion (`artifacts/readiness_gaps.json` +
`artifacts/check_readiness.py`) so the doc's claims are parseable and every gap row
links to a real grounding artifact path — and a test that fails if a row cites a
nonexistent artifact (prevents fabrication drift).

## Files to create (all task-namespaced — NO core edits)
- `experiments/ralph_outputs/J10/artifacts/lessons_from_production.md` — the section.
- `experiments/ralph_outputs/J10/artifacts/readiness_gaps.json` — structured gap registry.
- `experiments/ralph_outputs/J10/artifacts/check_readiness.py` — validator/renderer.
- `experiments/ralph_outputs/J10/artifacts/test_readiness.py` — pytest (groundings exist,
  no fabricated-metric tokens, schema valid).

## Dependencies
Python 3.13 stdlib only (json, pathlib, re). No network, no GPU, no cluster.

## Risks
- **R1 Fabrication creep.** Mitigation: every quantitative claim in the doc must trace to
  a grounding artifact; the test asserts cited artifact paths exist and bans invented
  prod-metric phrasing ("we deployed", "in production we observed", "X% MTTR reduction").
- **R2 Vacuous honesty** (all hedging, no content). Mitigation: each gap ships a concrete,
  runnable-in-principle validation protocol (shadow-mode design, distribution-shift
  trap-recall test, MTTR measurement plan), not just "we'd need more data."
- **R3 Overclaiming the sim.** Mitigation: explicitly cite A16's 7 broken scenarios and
  the engine's unmodeled metrics so the sim's limits are on the record.

## Success criteria
- `lessons_from_production.md` exists, reads honestly, fabricates NO production experience.
- The three required gaps (trap-action safety under distribution shift, shadow-mode, MTTR)
  are each present with a concrete validation protocol.
- Every grounding citation resolves to a real path; `check_readiness.py` confirms it.
- `test_readiness.py` passes under pytest.
- No shared core file edited (`rex/*`, `sim/*`, `agent/*`, `experiments/*.py`, dashboards).
