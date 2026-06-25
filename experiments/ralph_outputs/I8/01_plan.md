# 01 — Plan (Task I8)

## Objective
Write a rigorous, accurate theoretical comparison of three paradigms for aligning/steering LLM
behavior — **code-as-policy / auto-harness** (this project's approach), **RLHF** (reinforcement
learning from human feedback), and **Constitutional AI (CAI / RLAIF)** — across five axes:

1. Where knowledge lives
2. Verifiability
3. Sample efficiency
4. Safety guarantees
5. Interpretability

The comparison must be (a) technically correct about each paradigm and (b) *grounded* in this
repo's actual code-as-policy/harness implementation, not hand-waved.

## Approach
- Anchor the "code-as-policy" column in the real machinery here: a **frozen, swappable LLM**
  (`agent/llm.py`) wrapped by an **evolving code harness** (`rex/harness.py`, `rex/loop.py`,
  `rex/tree.py`) with a **deterministic, root-cause-aware reward** (`rex/scoring.py`:
  `0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap`) and a **safety gate**
  (`is_safe` / trust-tier registry). No weight updates — the policy is improved by changing
  *code around* the model and by Thompson-sampling refinements (`thompson_search`).
- Describe RLHF accurately: reward model trained on human pairwise preferences, policy optimized
  by PPO against it + KL penalty to a reference policy. Knowledge lands in **weights**.
- Describe Constitutional AI accurately: a written **constitution** (principles) drives
  AI-generated self-critiques/revisions (SL-CAI) and **RLAIF** (RL from an AI preference model);
  the human label is replaced by an AI label conditioned on principles. Knowledge lands in
  **weights + the constitution text**.
- Produce a single rigorous markdown doc + a structured machine-readable axis matrix (JSON/CSV)
  so the comparison is checkable, plus a tiny validator that asserts the matrix is well-formed.

## Files to create (all task-namespaced — no shared-core edits)
- `experiments/ralph_outputs/I8/artifacts/comparison.md` — the deliverable essay.
- `experiments/ralph_outputs/I8/artifacts/axes_matrix.json` — the 3×5 axis matrix, machine-readable.
- `experiments/ralph_outputs/I8/artifacts/validate_matrix.py` — validates JSON shape + that every
  cell is non-empty and citations resolve to real repo paths.
- The 10 step files + SUMMARY.md + result.json.

## Dependencies
- Python 3.13 stdlib only (`json`, `os`). No network, no GPU, no cluster. Self-contained.

## Risks
- **Inaccuracy risk** (the main one): mischaracterizing RLHF or CAI would fail the "be accurate"
  requirement. Mitigation: pin claims to well-established descriptions (Christiano 2017 / InstructGPT
  for RLHF; Bai et al. 2022 "Constitutional AI: Harmlessness from AI Feedback" for CAI) and avoid
  inventing numbers.
- **Overclaiming for code-as-policy**: it is NOT strictly superior — it inherits the frozen model's
  ceiling and only helps where a *verifier* exists. The doc must state this honestly.
- **Citation drift**: claims about "this project" must point at files that exist. Mitigation: the
  validator checks every cited repo path resolves.

## Success criteria
- `comparison.md` covers all 3 paradigms × 5 axes with correct, defensible characterizations.
- Code-as-policy column is grounded in named, real files in this repo.
- `axes_matrix.json` parses and `validate_matrix.py` exits 0 (shape + non-empty + paths-resolve).
- Honest limitations section (where code-as-policy loses).
