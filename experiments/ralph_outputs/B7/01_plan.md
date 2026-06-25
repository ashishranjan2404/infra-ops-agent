# 01 — Plan (Task B7: standalone root-cause accuracy metric)

## Objective
Add **root-cause accuracy** as a STANDALONE metric, decoupled from the
pass/fail graded reward. Today `rex/scoring.py` folds diagnosis into one number
(`0.30*diag + 0.25*fix + 0.45*resolved - traps`), so a correct diagnosis with a
botched fix is indistinguishable from a lucky fix with a wrong diagnosis. We want
diagnosis reported on its own.

## Approach
- Reuse the deterministic, hermetic stemmer `rex.scoring._stems` so category
  matching is phrasing-robust and consistent with the shipped diagnosis judge
  (no LLM, no network).
- Gold labels come from two authoritative sources already in the repo:
  1. Scenario YAML `root_cause.kind` / `root_cause.location`
     (`scenarios/cidg/generated/*.yaml`).
  2. `rex/harness.py:_KIND_CATEGORY` mapping kind -> one of 8 gold categories.
     The HUD trajectory export already labels each record with `true_category`
     using this taxonomy.
- Build a deterministic multi-class classifier: per-category discriminative
  keyword vocab, classify the agent's free-text answer, compare to gold.
- Report: overall accuracy, per-category recall, confusion matrix, and a
  decoupling check (how often root-cause-correct disagrees with pass/fail).

## Files to create (task-namespaced; NO shared-core edits)
- `artifacts/root_cause_accuracy.py` — the metric + CLI.
- `artifacts/test_root_cause_accuracy.py` — hermetic unit tests.
- artifacts run outputs (txt + json).

## Data
- Real: `opensre-traj/out/hud_trajectories.jsonl` (197 trajectories, `answer` +
  `true_category`, 8 categories).
- Grounding self-test: `scenarios/cidg/generated/*.yaml`.

## Dependencies
`rex.scoring._stems` (import, no edit). Optional `pyyaml` for the YAML self-test.

## Risks
- A keyword classifier on long verbose answers may over-fire on common terms
  (e.g. "rollback"/"deploy"). Mitigate with discriminative vocab + tie->unknown;
  document residual error honestly rather than tuning to a number.

## Success criteria
- Metric importable + runs on the 197 real trajectories producing a real number.
- Unit tests pass (classification, gold mapping, confusion, decoupling).
- No shared core file edited.
