# F7 — 01 Plan: Rebuttal-Anticipation Doc

## Objective
Write a reviewer-rebuttal-anticipation document for the SRE-Degrees project: enumerate the
top 8–12 likely reviewer attacks (AAAI/NeurIPS-D&B/ICLR-flavored), each stated in its
*strongest* form, paired with the *best honest response/mitigation*. The goal is not to spin
weaknesses away — it is to make the team's defense legible and to mark which attacks are
genuinely fatal vs. survivable.

## Approach
1. Ground every attack in the project's *real* weaknesses, not strawmen. Source of truth:
   - `ARCHITECTURE.md` (the thesis, the reward formula, the REx results table, curriculum).
   - `rex/scoring.py` (the 0.30/0.25/0.45/−0.60 reward, the LLM-judge on mechanism).
   - `opensre-traj/` (the FLAT RFT run: 0.522 → 0.491 over 25 steps).
   - Scenario inventory: ~51 CIDG YAML + 19 reconstructed real-outage JSON specs; 5 hard
     incidents in the headline REx sweep; 5 frozen models.
2. The known weaknesses to ground in (from the dispatch): **synthetic data, small N, flat RFT,
   reward-hacking, single domain.** Plus what the architecture itself concedes (0.86 is a
   *mechanical* ceiling; gateway-routed models; LLM-judge in the loop).
3. For each attack: (a) steelman it, (b) give the honest response, (c) classify severity
   (FATAL-IF-TRUE / SERIOUS / MANAGEABLE) and what evidence would close it.
4. Add a "concession ledger" — the 3–4 things we should just admit up front in the paper.

## Files to create
- `experiments/ralph_outputs/F7/artifacts/rebuttal_anticipation.md` — the deliverable.
- `experiments/ralph_outputs/F7/artifacts/attacks.json` — machine-readable index of attacks
  (id, title, severity, one-line response) so it can be linted/sorted.
- `experiments/ralph_outputs/F7/artifacts/validate_attacks.py` — validates attacks.json
  schema + asserts the doc covers every required weakness theme. This is the "test."
- The 10 ralph step files + SUMMARY.md + result.json.

## Dependencies
- Read-only: `ARCHITECTURE.md`, `rex/scoring.py`, scenario/spec counts. No core-file edits.
- Python 3.13 stdlib only (`json`) for the validator.

## Risks
- **Risk: doc becomes a puff piece** (attacks too weak). Mitigation: each attack must cite a
  real number or design choice the project can't easily change; ouroboros step filters soft ones.
- **Risk: responses overclaim** ("we already solved this"). Mitigation: severity tags force
  honesty; FATAL-IF-TRUE items get "what we'd need to do," not "we're fine."
- **Risk: not grounded** in actual repo numbers. Mitigation: pull exact figures (0.522→0.491,
  0.86 = (4×1.0+0.30)/5, −0.60 trap, 5 models, 5 hard incidents).

## Success criteria
- 8–12 attacks, each with steelman + honest response + severity + closing evidence.
- Every required weakness theme present: synthetic data, small N, flat RFT, reward-hacking,
  single domain (validator enforces this).
- `attacks.json` parses; `validate_attacks.py` exits 0.
- A concession ledger and a "what would actually sink the paper" section exist.
