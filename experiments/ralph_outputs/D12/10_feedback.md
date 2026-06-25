# D12 — 10 Feedback for next task

The `--group` smoke (`--tasks 0,1 --group G --steps 1 --smoke`) runs in ~2 min and is the cheapest
way to prove training-config plumbing against the live HUD harness without burning the compute cap —
use it for any RFT-knob task (group, lr, tasks, reset-head). Two gotchas to carry forward: (1) the
trainable slug `opensre-qwen3-8b` currently 404s — it must be forked (`hud models fork Qwen/Qwen3-8B
--name ...`) before any real run, though the smoke still emits rollouts via fallback; (2) ground all
variance/statistics claims in the real logs under `opensre-traj/runs/*.jsonl` (rollouts are
task-major, group_size consecutive entries per task) rather than asserting numbers — the per-task
within-group sigma (~0.069) is the quantity GRPO advantage actually rides on, and it's much smaller
than the per-step cross-task std (~0.183), so don't confuse the two. When a knob only changes
gradient/estimator quality (like group size), say so explicitly and don't let it masquerade as a fix
for a flat-reward root cause (which for opensre is task-count + reward headroom, per the v2 diagnosis).
