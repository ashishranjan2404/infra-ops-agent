# E3 — 06 Implementation

## What I built (all under `experiments/ralph_outputs/E3/artifacts/`)
1. **`eval_three_way_cascade.py`** — the 3-way cascade comparison harness.
   - Selects **14 cascade incidents** deterministically: `sorted(scenarios_by_family()["cascade"])[:14]`.
   - Three arms: `zero_shot` (base `Qwen/Qwen3-8B`), `opensre_trained`
     (`opensre-qwen3-8b-1e439a`, the OpenSRE GRPO/RFT forked slug), `fireball_trained`
     (**blocked**, no model).
   - Reuses the repo's REAL machinery: `rex.harness.load_scenario/run_plan`,
     `rex.loop.build_prompt/parse_plan`, `rex.scoring.score_plan` (P0 **deterministic** judge),
     `experiments.compute_pass_at_k` (pass@k + Wilson CI).
   - Reaches the two open models by **gateway slug**. Because those slugs are NOT in
     `agent/models.ROSTER`, the harness registers them into a **local runtime copy** via
     `ROSTER.setdefault(...)`. **`agent/models.py` is never edited** (Ralph hard rule).
   - `--dry-run` selects incidents + probes arm reachability with no scoring calls.
2. **`test_eval_three_way_cascade.py`** — 6 network-free tests (selection, arm wiring, local
   roster registration, summarize stats).
3. **`result_three_way.json`** — the real run output (56 episodes, 0 errors).
4. **`dryrun_three_way.json`** — selection + reachability probe output.

## Real artifacts produced (not placeholder)
- 14 selected cascade incidents (deterministic, all `family=cascade`).
- A real eval: **56 episodes** (14 incidents × 2 runnable arms × 2 seeds), 0 errors, 64s.
- Deterministic per-incident rewards for both runnable arms.

## The Fireball blocker (documented, NOT fabricated)
The `fireball_trained` arm has `roster_key=None` and `status="blocked"`. There is **no Fireball
training dataset and no forked Fireball model**: the upstream Fireball pipeline tasks
(`experiments/ralph_outputs/E2`, `D8`) are empty (E2 has no files; D8 has only an empty
`artifacts/` dir). The harness records this arm as blocked with the reason string and **emits no
numbers** for it. The comparison table prints `BLOCKED` in that row.

## Design notes / caveats (from grill + ouroboros)
- **Apples-to-apples:** zero-shot uses the exact base model OpenSRE was forked from (`Qwen/Qwen3-8B`)
  so the comparison isolates *training*, not model identity.
- **Single-proposal, deterministic judge** isolates the policy (no REx search, no LLM judge) →
  reproducible.
- **Caveats:** reasoning-model `<think>` output can cap `parse_plan` yield (affects both arms
  symmetrically); gateway sampling-default parity between base and forked slug isn't fully
  controllable from here; a 200 proves reachability, not checkpoint identity (recorded `model`
  string for audit).
- **No shared-core edits.** Confirmed by `git status` (only new files under E3/artifacts).
