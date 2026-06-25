# D2 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — Backend integration engineer
**Problems found:**
- A1. `preflight()` parses CLI table text, not a structured API. Table rendering can change
  between hud-python versions → brittle string matching. Real bug risk.
- A2. The "14B present" check excludes `a17b` but what about future `*-14B-A2B` MoE names? The
  substring logic could mislabel.
- A3. `_load_gateway_models()` is defined but unused (preflight uses the CLI path). Dead code.

**Resolutions:** A1 accepted as a known limitation — but the CLI is HUD's *stable contract*
(SDK list helper varies by version), so CLI parsing is actually the safer choice; documented
in the critique. A2: narrow — there is currently no 14B of any kind; the A17B exclusion is the
only real false-positive observed. Acceptable, noted. A3: real — `_load_gateway_models` is
dead; keep it only if it adds value. **Decision: leave it but mark it; it documents the SDK
path we deliberately avoided. (Minor; not worth a core-adjacent refactor under time cap.)**

## Engineer B — RL training engineer
**Problems found:**
- B1. The launcher claims "imports v2, never edits core" — but `_run_training` does `os.chdir`
  into opensre-traj. If two Ralph workers import this concurrently, chdir is process-global.
  Real concern for parallel safety.
- B2. `--smoke` bypasses the preflight-guard abort (`rc!=0 and not smoke`). So a smoke run
  against a non-existent base would proceed to fork-time failure. Is that intended?
- B3. No seeds / determinism note: a "14B vs 8B" comparison needs matched protocol; the config
  asserts success criteria but the launcher doesn't enforce them.

**Resolutions:** B1 real but bounded — each Ralph worker is its *own process* (separate
dispatch), so process-global chdir is fine here; flagged for any in-process multiplexing.
B2: intentional and documented — smoke is meant to surface the downstream fork/SDK error
loudly rather than be blocked by preflight; the BLOCKER text still prints. Keep. B3: accepted
as a real gap — protocol matching is a *run-time* discipline, not enforceable by a launcher;
moved to config `success_criteria` + critique. Not fabricating the comparison is the win.

## Engineer C — Reviewer / skeptic
**Problems found:**
- C1. The whole deliverable is "the model doesn't exist, here's a substitute." Is that a
  cop-out? Could we have forked 27B and at least smoke-trained?
- C2. The config's `requested: Qwen/Qwen3-14B` — is that a real HF model id, or invented?
- C3. "8B too small" is asserted from one flat run; the doc should not overstate causation.

**Resolutions:** C1: a real smoke fork+1-step of 27B is *paid Tinker forward/backward* and
genuinely out of the ~15-min cap; the preflight proving the substitute is trainable (exit 0)
is the honest, runnable evidence we CAN produce now. Documented as the explicit boundary.
C2: `Qwen/Qwen3-14B` is a plausible HF-style id but is NOT on our gateway and was not asserted
to exist there — config marks `available: false`. We do not claim it as runnable. C3: the
plan/config say 8B was *flat* (a fact from the JSONL) and frame size as a *hypothesis/lever*,
not proven cause. Wording kept conservative.

## Final filtered spec (deltas applied)
- Keep CLI-parse preflight (stable contract); document the brittleness limitation.
- Keep `--smoke` bypass as an intentional loud-fail path (documented).
- Keep dead `_load_gateway_models` as documentation of the avoided SDK path (low cost).
- Do NOT fabricate a 14B run or a smoke curve; preflight exit-0 on the substitute is the
  real, reproducible evidence. Comparison protocol lives in `success_criteria`, run-time.
