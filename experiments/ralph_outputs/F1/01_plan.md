# 01 — Plan (Task F1: Full Related Work section)

## Objective
The paper's Related Work (§2 of `experiments/PAPER_OUTLINE.md`) is currently a thin
bullet list. Produce a **complete, prose Related Work section** in markdown with
**real, accurate citations** covering: CWM (code-world-models), AutoHarness,
REx/refinement-tree, SREGym, Constitutional AI, RLVR/GRPO — plus the adjacent works
the paper actually leans on (AIOpsLab/ITBench, FIREBALL, LLM-as-judge, pass@k,
McNemar/Wilson). Ground every claim in `PAPER_OUTLINE.md`, `PAPER_QUESTIONS.md`, and
the repo so each citation is positioned correctly against our three claims (C1 harness,
C2 transfer, C3 SME-feedback RLVR).

## Approach
1. Read the grounding: `experiments/PAPER_OUTLINE.md §2/§5/§6`, `PAPER_QUESTIONS.md §6–10`.
2. Read the repo to make each cite's positioning *true to our implementation*:
   - `rex/harness_synth.py` — AutoHarness framing (search over rules-as-data, held-out acc).
   - `rex/tree.py` — REx Thompson-tree (Beta posterior per node).
   - `rex/scoring.py` — deterministic diagnosis judge (RLVR / no-LLM-judge claim).
   - `rex/loop.py`, `rex/harness.py`, `sim/engine.py` — code-as-policy / world-model framing.
3. For each work: one accurate sentence of *what it is*, then *what we borrow vs. what
   is new*. Avoid over-claiming; flag hypotheses (C2 transfer) as pending.
4. Add a positioning summary table and a statistical-methodology subsection.

## Files to create (task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/F1/artifacts/related_work.md` — the deliverable.
- `experiments/ralph_outputs/F1/artifacts/check_related_work.py` — validator (markdown
  parse, required-citation coverage, link/heading sanity).
- The 10 step files + SUMMARY.md + result.json.

## Dependencies
- None runtime-heavy. Pure doc + a stdlib-only Python validator. No API keys, no cluster.

## Risks
- **Citation accuracy.** Wrong author/venue/claim on a real paper is the biggest reviewer
  attack. Mitigation: describe each work by its *mechanism* (verifiable against our own
  knowledge) and keep venue/year conservative; mark the AutoHarness/REx names as the
  framing the repo itself uses (the code comments name them) rather than over-asserting a
  canonical citation that may not match.
- **Knowledge-cutoff uncertainty** on very recent works (CWM 2025, SREGym 2026). Mitigation:
  ground SREGym's arXiv id from `PAPER_QUESTIONS.md` (2605.07161); describe CWM by its
  public thesis (predict code-execution effects → world model) which is stable.
- **Over/under-engineering.** It's a prose section; the only "test" is parse + coverage.

## Success criteria
1. `related_work.md` parses as markdown, has a `## 2. Related Work` heading + subsections.
2. Every required citation present and *correctly positioned* vs C1/C2/C3.
3. Validator passes (coverage + structure).
4. No shared core file edited.
