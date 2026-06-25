# E3 — 01 Plan

## Objective
Build and run a **3-way comparison eval harness** that scores three policies on the
**14 hardest cascade incidents**:
1. **zero-shot** — base open model, untrained.
2. **OpenSRE-trained** — same base model after OpenSRE GRPO/RFT.
3. **Fireball-trained** — BLOCKED (no Fireball data/model; see E2/D8).

Deliver the harness, run what is runnable (zero-shot + OpenSRE if reachable), and
document the Fireball-model blocker. **Do not fabricate Fireball numbers. Do not edit
shared core files.**

## Approach
- Reuse the repo's real machinery instead of reinventing it:
  - `rex.harness.scenarios_by_family()` → the `cascade` family (20 incidents); take 14 deterministically.
  - `rex.harness.load_scenario` / `run_plan` → the simulator.
  - `rex.loop.build_prompt` / `parse_plan` → prompt + plan parse.
  - `rex.scoring.score_plan` / `failed_checks` → the **P0 deterministic judge** (reproducible, no LLM judge).
  - `experiments.compute_pass_at_k` → unbiased pass@k + Wilson CI.
- A new standalone harness `eval_three_way_cascade.py` in my artifacts dir.
- The OpenSRE-trained and base models are reached by **gateway slug**, NOT in
  `agent/models.ROSTER`. Rather than edit `agent/models.py` (forbidden shared file),
  the harness registers the two slugs into a **local runtime copy** via `ROSTER.setdefault`.
- Threshold 0.8 (pass = SLO restored + root cleared + no trap), same as `rex.eval_pass_at_k`.

## Files to create (all task-namespaced)
- `artifacts/eval_three_way_cascade.py` — the harness.
- `artifacts/test_eval_three_way_cascade.py` — network-free tests (selection, arms, stats).
- `artifacts/result_three_way.json` — the run output.
- `artifacts/dryrun_three_way.json` — selection + reachability probe.

## Files to modify
None. No shared core file is touched.

## Dependencies / reachability
- `HUD_API_KEY` (gateway), `requests`, Python 3.13. Base + OpenSRE slugs served on
  `https://inference.beta.hud.ai`.

## Risks
- **Fireball arm has no model** → blocked by design; record honestly, no fake numbers.
- The OpenSRE training run was previously **FLAT** (~0.49–0.51 mean) — expect a small or
  null lift over zero-shot, not a dramatic one. Report it honestly.
- Reasoning model (`<think>`) latency; keep seeds modest.

## Success criteria
- Harness selects exactly 14 distinct cascade incidents.
- Runs the runnable arms end-to-end with the deterministic judge, 0 fabricated numbers.
- Fireball blocker documented; tests pass; result.json written.
