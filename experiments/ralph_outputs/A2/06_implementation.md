# A2 — 06 Implementation

## What I built
A single, self-contained, **task-namespaced** runner that completes the 750-episode
ablation with a faster/cheaper proposer, without editing any shared core file.

### `artifacts/run_ablation_fast.py` (NEW)
Thin wrapper over the canonical engine `rex/eval_pass_at_k.py`:
- Imports `run_eval`, `print_report`, `CONDITIONS`, `summarize`, `pick_incidents`,
  `floor_check` — does **not** reimplement scoring or rollout logic.
- Default proposer `deepseek-v4-pro` (cheaper/faster API via HUD gateway; chosen by
  measurement — see 07. `claude-haiku-4-5` 400s, `minimax-m3` returns empty, `gemini-3.1-pro`
  ~14s/call).
- `--max-seconds` wall-clock budget implemented with a `_Deadline` SIGALRM context manager;
  on expiry it raises `TimeoutError`, caught to build a **real** partial report from the
  on-disk checkpoint (`_summarize_partial`) — never fabricated.
- `completed_episodes` is counted from actual `per_incident_rewards`, so aborted/mid-flight
  episodes are never miscounted as done.
- `a2_meta` block records `target_episodes`, `completed_episodes`, `fully_completed`,
  `wall_seconds`, `fast_model`, and an honest `note`.
- Output schema is identical to `run_eval`'s, so `rex/run_ablation_v2.py` (McNemar) can
  consume the result unchanged.

### Judge: FROZEN
Reward is the **P0 deterministic judge** (`rex/scoring.py` via `score_plan(..., judge_fn=None)`),
inherited unchanged. Only the proposer model varies — the ablation's internal contrasts
(rex vs best_of_n vs retry_realistic vs rex_no_oracle) stay valid and reproducible.

## Shared-file changes I did NOT make (proposed, not applied)
None required — the wrapper composes the existing API. If one *wanted* to fix the underlying
issue at the source, the minimal change would be to `rex/eval_pass_at_k.py::run_eval` to
checkpoint more frequently and flush on signal; I deliberately did **not** touch that shared
file (parallel-safety rule). The wrapper achieves the same outcome externally.

## How to run
```bash
set -a; source ~/.zshrc; set +a
python3 experiments/ralph_outputs/A2/artifacts/run_ablation_fast.py \
    --model deepseek-v4-pro --per-family 10 --seeds 5 --max-workers 16 --max-seconds 3300
# resumes automatically from artifacts/ablation_pass_at_k_deepseek-v4-pro.json.partial
```

## Bug found & fixed during build
The first smoke run (`--max-seconds 120`, 6 eps) timed out before the engine's first
25-episode checkpoint flush, so `_summarize_partial` returned `None` and the script printed
`[error] nothing produced`. Fixed: the empty-checkpoint case now emits a valid empty report
(`0/750 completed`) and `print_report` is guarded against empty `by_condition`.
