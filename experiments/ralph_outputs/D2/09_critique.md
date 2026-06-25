# D2 — 09 Critique (honest)

## The headline negative result
The task — "run RFT with Qwen-14B" — **cannot be literally executed**: the HUD Tinker
gateway has no Qwen-14B (dense or MoE). This is the dominant finding. Everything I built is
the honest fallback: a launcher + config + verified preflight + a substitute, not a trained
14B model. A reviewer is right to note no model was actually trained.

## What a reviewer attacks
1. **"You delivered scaffolding, not a run."** True. The blocker (no 14B) plus the ~15-min
   compute cap means a real fork + 30-step GRPO on the 27B substitute (hours of paid Tinker
   forward/backward) was out of scope. The strongest *real* evidence I could produce is the
   live preflight proving the substitute is trainable (exit 0). I chose that over a fabricated
   curve — per the brief's "honest blocker beats fake numbers."
2. **"27B is not 14B — it's ~2x the asked size."** Correct, and the config says so explicitly.
   There is no clean 14B stand-in on this backend; the closest *dense* rung above 8B is 27B.
   The MoE alt (30B-A3B, ~3B active) is cheaper but a different architecture class.
3. **"The premise '8B too small' is from one flat run."** Fair. `train_qwen3-8b_v2.jsonl`
   (0.50→0.54 over 15 steps) shows flatness, but that could be reward-shape ceiling, not
   capacity. I framed size as a *hypothesis/lever*, not proven cause. A clean test would also
   re-examine the v2 reward headroom before paying for 27B.
4. **Brittle preflight.** It parses `hud models list` text, not a structured SDK call. Table
   format could change across hud-python versions. Mitigated by `COLUMNS=400` and the CLI
   being HUD's stable contract, but it's a string-matching dependency.
5. **`--reset-head` hazard inherited from core.** `train_rft_v2.py` swallows reset-head
   failures and would continue from an undefined head on a fresh fork. I did NOT fix this
   (no core edits under parallel execution) — documented as a follow-up. If someone runs the
   real 27B job, they must confirm the fork's checkpoint tree before trusting `--reset-head`.

## What's weak / missing
- No actual training metrics (by design + blocker).
- No multi-seed protocol enforced (it lives in `success_criteria`, run-time discipline).
- Dead `_load_gateway_models()` kept as documentation of the avoided SDK path.

## What's solid
- The blocker is a **real, reproducible gateway fact**, not a guess.
- The launcher is runnable, exit-code-correct across 4 scenarios, and touches **zero** shared
  core files — it imports the proven v2 trainer.
- The substitute path is *verified trainable*, so this is one `hud models fork` away from a
  real run the moment compute/approval lands.
