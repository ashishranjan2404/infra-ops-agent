# D7 — 01 Plan

## Objective
Answer the question: **does training on cascade incidents only hurt simple-incident
performance and help cascade-incident performance?** Deliver (a) a runnable
cascade-only "training" config and (b) an eval harness measuring **simple vs cascade
pass@1 transfer**.

## Key reality (sets the whole approach)
This repo is **code-as-policy / auto-harness over a FROZEN LLM** (per project memory:
"NOT Qwen fine-tuning"). There are no gradient steps in the local loop. The lever that
plays the role of "training data" is the **in-context exemplar pool** injected into the
proposer prompt (`rex/loop.py:build_prompt`). So:

> "Train on cascade incidents only" == build the few-shot exemplar pool **exclusively
> from the cascade family**, then evaluate held-out pass@1 on simple AND cascade.

This is the faithful, cheap, reproducible analog of an RFT data-mix ablation. The
eval harness is identical whether exemplars come from prompts or a real fine-tune,
so the deliverable survives a future real training run (swap the proposer, keep eval).

## Approach
1. Reuse the existing benchmark: `scenarios/cidg/generated/registry.json` self-labels
   families. Counts available: **simple=12, cascade=20, novel=10**.
2. Reuse the **deterministic judge** (`rex.scoring.score_plan`) + `run_plan` so the
   metric is reproducible (no LLM judge).
3. Reuse `pass@k` + Wilson CI from `experiments/compute_pass_at_k.py`.
4. New code only injects an **exemplar prefix** before `build_prompt(...)`. Three
   configs: `cascade` (cascade-only pool), `mixed` (all families), `none` (zero-shot
   prior). The 3-way contrast is the experiment.
5. **Train/eval split with a hard leakage guard**: exemplars are removed from the
   eval set.
6. Report per (config, eval-family): pass@1, Wilson 95% CI, mean reward, reward std.
   Headline = transfer deltas H1 (helps cascade) and H2 (hurts simple).

## Files to create (all task-namespaced — NO shared core edits)
- `artifacts/d7_cascade_only.yaml` — the cascade-only training config.
- `artifacts/d7_train_eval.py` — the train+eval harness (exemplar injection + pass@1).
- `artifacts/d7_results*.json` — produced outputs (dry-run + real smoke).

## Dependencies
- Core (read-only): `rex.harness`, `rex.loop`, `rex.scoring`, `compute_pass_at_k`.
- `agent.llm.call` for the frozen proposer (gateway, `HUD_API_KEY`).
- Optional `pyyaml` (harness has a mini-YAML fallback so it runs without it).

## Risks
- **Compute cap (~15 min).** Full budget = 3 configs × 2 families × 4 incidents × 3
  seeds = 72 calls; may overrun. Mitigation: `--dry-run` proves wiring with zero
  network; a reduced "smoke" config proves the real path; full run is documented as
  scalable when more compute is available.
- **Under-powered.** With ~12–24 episodes/cell, Wilson CIs are wide; deltas may be
  CI-overlapping. We report CIs honestly rather than over-claim.
- **Frozen-LLM caveat.** In-context exemplars are a *proxy* for fine-tuning; the
  direction of transfer is suggestive, not a gradient-trained result. Stated up front.

## Success criteria
- Config + harness exist, syntax/YAML-valid, importable.
- Dry-run produces a real split with **zero train/eval leakage**.
- A real (reduced) run produces real pass@1 + Wilson CI per (config, family).
- Transfer deltas H1/H2 computed and reported with honest CIs.
