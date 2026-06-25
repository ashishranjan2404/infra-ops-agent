# C3 — 01 Plan

## Objective
Run the AutoHarness-style rule synthesis (`rex/harness_synth.py`) on **only novel
incidents** (a strict generalization test), and report whether the synthesized
safety rules generalize to novel incidents held out from synthesis.

## Why this is the real test
The default `rex/harness_synth.py` split mixes seen/unseen vendor incidents. C3
restricts the *entire* experiment to the A8 strict-novel set: 15 cidg incidents that
A8 certified have **zero overlap** with the policy's training trajectories
(exact-id + token-pair + company-axis novelty). Every example here is novel w.r.t.
the training corpus. We then split those 15 into TRAIN (10) / HELDOUT (5) so a
spanning hazard appears in both → genuine cross-incident generalization, not lookup.

## Approach
1. Read the A8 novel universe from `experiments/ralph_outputs/A8/artifacts/heldout_manifest.json`.
2. Confirm all 15 ids load through `rex.harness.load_scenario` and produce labeled
   examples via the unmodified `rex.harness_synth.labeled_examples`.
3. Compute hazard coverage; pick a TRAIN/HELDOUT split where the GENERALIZABLE hazard
   `treats_forbidden_category` (an interpreter-expressible feature) spans both splits.
4. Run Thompson-tree synthesis (`rex.tree.thompson_search`) using the shared
   `propose_ruleset` mutation operator + `train_score` reward — TRAIN labels only.
5. Score the best rule-set on TRAIN and HELDOUT; compare to seed (empty) and the
   hand-written `is_safe` baseline. Report held-out mistakes + leakage check.

## Files to create (all task-namespaced)
- `artifacts/run_novel_synth.py` — runner that IMPORTS (does not edit) `rex/harness_synth.py`.
- `artifacts/novel_synth_result.json` — emitted metrics.

## Files I will NOT modify
Shared core: `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, A8's dir,
`scenarios/cidg/generated/*` (read-only).

## Dependencies / env
`python3`, `pyyaml`. LLM mutation operator: default `claude-haiku-4-5` is out of
Anthropic credits in this env (HTTP 400) → use the HUD gateway model `gpt-5.5`
(verified working). Synthesis is model-agnostic; any JSON-rule emitter works.

## Risks
- The dominant blockable hazard `trap_action` is a per-scenario spec list with NO
  general feature → synthesized rules over the 6 known features cannot capture it
  directly; they can only catch the subset that also trips a known feature. This is
  a scope limit to report honestly, not hide.
- `leak_restart` is single-incident (media_oom_leak) → lands in HELDOUT as
  unseen-in-train → expected false-allows; report as out-of-scope.

## Success criteria
- Synthesis runs on novel-only TRAIN, emits a real rule-set + metrics JSON.
- Held-out (novel) accuracy + false-allow rate reported vs. both baselines.
- Leakage check passes (TRAIN/HELDOUT disjoint, held-out labels untouched in search).
- No shared core file edited.
