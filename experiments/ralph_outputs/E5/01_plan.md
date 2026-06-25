# E5 — Plan: Fireball transfer on 10 novel incidents (generalization test)

## Objective
Measure how the **Fireball** transfer-target policy generalizes to incidents it has
never seen, by running a zero-shot transfer eval on a 10-incident **novel held-out
set** with strict zero training overlap. Read Fireball's number against real baselines.

## Approach
1. **Reuse the A8 novel set.** A8 already produced a strict held-out split
   (`experiments/ralph_outputs/A8/artifacts/heldout_manifest.json`) with tiered
   novelty (exact-id + token-pair + company-axis). Select 10 incidents with
   `held_out == true`, novel-family first, then back-fill from held-out simple. Do
   NOT invent a new set.
2. **Build a transfer-eval harness** (`transfer_eval_novel.py`) that imports the
   frozen core (`rex.harness`, `rex.scoring`, `rex.loop`, `agent.llm`) and runs any
   roster policy zero-shot over the set, scored by the **P0 deterministic judge** (no
   LLM-judge noise). Binary pass at reward >= 0.8; report pass@1 + Wilson 95% CI,
   mean reward, within-group std.
3. **Run available baselines** (e.g. `glm-5p2` on Fireworks) + two no-network
   controls: `empty` (floor) and `oracle` (ceiling).
4. **Fireball is blocked.** Fireball is not a roster/reachable model in this repo.
   Record it as `status=blocked` with the concrete reason; never fabricate a number.

## Files to create (all task-namespaced, no core edits)
- `experiments/ralph_outputs/E5/artifacts/transfer_eval_novel.py` — the harness.
- `experiments/ralph_outputs/E5/transfer_results.json` — real run output.
- `01..10` + `SUMMARY.md` + `result.json`.

## Dependencies
- A8 manifest (present). `rex/*` + `sim/*` frozen core (read-only). `agent/llm.py`
  for reachable baselines (`HUD_API_KEY`, `FIREWORKS_API_KEY` from `~/.zshrc`).

## Risks
- **Fireball unavailable** → primary expected blocker; deliver harness + baselines.
- Some gateway models return empty / Anthropic out of credits → record as blocked
  per-policy, don't drop silently.
- Key mismatch between A8 cidg_keys and rex registry → assert loadable, skip+warn.

## Success criteria
- Harness runs end-to-end on the 10 novel incidents.
- At least one real baseline produces real pass@1 + CI numbers.
- Floor (empty pass@1==0) and ceiling (oracle pass@1==1) controls hold.
- Fireball blocker documented honestly with the exact reason.
