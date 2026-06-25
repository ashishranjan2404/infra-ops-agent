# 01 — Plan (H4: experiment tracking shim)

## Objective
Give every eval/train run in the SRE-Degrees repo a single, lightweight way to record
its config + per-step metrics. Use Weights & Biases (or Trackio, a W&B-compatible
logger) when available; fall back to a local JSONL file otherwise. Provide an
integration guide (patch/snippet, not a core edit) and unit-test the fallback.

## Approach
- A self-contained `exptrack.py` module with a 4-method API: `init / log / summary /
  finish`, plus context-manager support. Backend chosen by env var with `auto` default.
- The JSONL backend is stdlib-only and is the path the tests exercise (no network).
- All methods are **best-effort**: they must never raise, so a missing/offline tracker
  can't abort a 30-step GRPO run.
- Integration delivered as a verified `.patch` against `opensre-traj/train_rft_v2.py`
  (the real train loop) + a snippet for `rex/eval_pass_at_k.py` — NOT applied to core.

## Files to create (all task-namespaced under H4/artifacts/)
- `exptrack.py` — the shim.
- `test_exptrack.py` — pytest + standalone runner for the JSONL fallback.
- `INTEGRATION_GUIDE.md` — where/how to call it in eval & train loops.
- `train_rft_v2.exptrack.patch` — verified-applyable patch (not applied).

## Dependencies
None required (stdlib only for the fallback). Optional: `wandb` or `trackio` if present.

## Risks
- Tracking code crashing a real training run -> mitigate with blanket best-effort guards.
- W&B not installed in this env -> that's fine, it's exactly the fallback we test.
- Editing a shared core file -> forbidden; deliver as patch + `git apply --check`.

## Success criteria
1. `exptrack.py` imports with zero non-stdlib deps and selects `jsonl` here.
2. JSONL run writes valid meta+metric+summary lines; auto-incrementing step works.
3. Unit tests pass (pytest + standalone).
4. Patch applies cleanly (`git apply --check`) without modifying the core file.
5. Integration guide shows exact call sites in both loops.
