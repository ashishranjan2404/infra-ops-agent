# E9 — 06 Implementation

## What was built (real, runnable, offline)

### 1. `artifacts/synth_sre_augmenter.py`
A dependency-light (PyYAML + stdlib) **synthetic SRE trajectory augmenter** over the CIDG
scenarios. For each scenario YAML it:
- extracts the gold label (`root_cause`, `canonical_fix.steps[0]`, `trap_actions`);
- emits, per variant, **1 positive** trajectory (correct read-only investigation → canonical
  fix, ends with `slo_breached:false, root_cleared:true`) and **3 graded negatives**
  (`negative_trap` using a real trap tool, `negative_wrong_fix`, `negative_empty`);
- assigns reward via the **mirrored `rex/scoring.py` rubric** (`0.30/0.25/0.45/−0.60`);
- applies **seeded, label-preserving perturbations** (alert-summary paraphrase + read-only
  tool-order shuffle), so variants are not photocopies but the gold label is invariant;
- guarantees **within-group reward spread > 0** (the unit of trainability).
- Includes a hermetic `--self-test` (no files, no network).

### 2. `artifacts/compare_arms.py`
The **head-to-head harness**. Scores each arm on a shared metric vector
`{n_trajectories, label_coverage, mean_within_group_spread, domain_match, floor_check}`:
- **synthetic arm** — fully scored from the augmented JSONL;
- **fireball arm** — `status:blocked` (with the threefold blocker text), unless a real
  FIREBALL export is dropped at `--fireball-jsonl`, in which case it is scored on the
  identical vector (with `domain_match=0`, D&D being off-domain).
- `decide()` emits a winner + reasons + an explicit anti-misreading `caveat`.

### 3. Real outputs generated
- `artifacts/augmented_trajectories.jsonl` — **51 scenarios → 204 groups → 816 trajectories**,
  all 204 groups have positive within-group spread (mean spread 0.5745).
- `artifacts/comparison_result.json` — the scored head-to-head + verdict.

## Shared-core safety
No shared core file was edited. The reward weights are **re-declared as local constants with
a source citation** rather than imported, keeping the augmenter offline and the original
`rex/scoring.py` untouched. All artifacts live under `experiments/ralph_outputs/E9/`.

## Fireball arm — why it is a scaffold + blocker, not a result
1. The FIREBALL D&D dataset is **not vendored** in this repo and fetching it is out of scope
   for an offline worker.
2. This project is **code-as-policy with a FROZEN LLM** (per project memory) — there is **no
   fine-tuning / transfer stack** to "transfer into." "Fireball transfer" presupposes training
   we do not run.
3. FIREBALL is **D&D combat state**, structurally analogous but **semantically off-domain**
   for k8s SRE diagnosis (`domain_match=0`).
The harness is nonetheless **wired** to score a real export on the same metrics if provided.
