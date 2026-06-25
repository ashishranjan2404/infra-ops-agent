# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — "Adversarial QA" (finds gaps)
**Problem found:** The spec's verifier check #1 (`branch_present`) keys off filename globs
`*grpo*`/`*fireball*`. But the in-repo files are named `train_rft.py` (RFT, not "grpo" in the
name) and there is NO file with "fireball" today. So check #1 could *false-positive* on our
OWN pre-existing `train_rft*` if I'm not careful, or *false-negative* if Wenji names her data
`dnd_traj.jsonl`. **Fix:** verifier must (a) snapshot the pre-existing inventory paths and
exclude them, and (b) match the corpus by *content/role*, accepting an explicit
`E1_MANIFEST.json` Wenji drops in, rather than guessing her filenames.

**Problem found:** Exit code 2 "blocked" vs 1 "error" — the Ralph harness may treat any
non-zero as failure. **Fix:** document the exit-code semantics in the script header and in
`07_test_results.md`; the verifier is *expected* to exit 2 today (that's the correct blocked
state), not a crash.

## Engineer 2 — "Scope hawk" (over/under-engineering)
**Problem found (over-engineering):** size_scan and LFS detection add complexity for a check
that the manifest doc already mandates by policy. Is a 25 MB heuristic worth code? **Decision:**
keep it but make it a *warning* (never flips the gate), because a fat checkpoint accidentally
committed is the single most likely way this push breaks `git clone` for the team — cheap
insurance, doesn't gate.

**Problem found (under-engineering):** spec never says HOW we confirm reward parity once
trajectories land. The verifier checks trajectories *exist* but doesn't re-grade. **Decision:**
correct to leave re-grading to gate-2 (it needs the model/env, out of scope for a stdlib
read-only verifier) — but `06`/the manifest must state the exact re-grade command so it's not
hand-wavy. Added: "we re-grade Wenji's trajectories via `rex.scoring` and assert
|our_reward − her_reward| < ε per rollout."

## Engineer 3 — "Reproducibility/realism" (untested edges, honesty)
**Problem found:** The whole deliverable assumes Wenji's branch EXISTS and is pushable. What
if her run was on an ephemeral HUD job whose artifacts have since expired? Then "push the
branch" is itself impossible and the true ask is "re-run and then push." **Fix:** the request
message must include a fallback path ("if the slug/job has expired, here's the re-fork +
re-run recipe") so the message is actionable in both worlds. This is the honest edge.

**Problem found:** I claim parity against "the in-repo deterministic judge" but our own
existing run logs (`runs/*.jsonl`) show the v2 reward is a blended mechanism+category score,
and `train_rft.py` v1 used a *different* reward than v2. So "THE judge" is ambiguous. **Fix:**
pin parity to `hud_env_v2.py` / `rex/scoring.py` (the v2/deterministic path) explicitly and
note v1 is not the parity reference.

## Final filtered spec (deltas applied)
1. Verifier reads an optional `E1_MANIFEST.json` Wenji drops in (filename-agnostic), and
   excludes the pre-existing inventory snapshot from "new branch" detection.
2. Exit-code semantics documented; exit 2 = legitimately-blocked, not error.
3. size_scan is warn-only; never flips the gate.
4. Manifest + `06` state the exact gate-2 re-grade command and ε tolerance.
5. Request message includes the "slug/job expired → re-fork & re-run" fallback.
6. Parity reference pinned to the v2 / `rex/scoring.py` deterministic path; v1 excluded.
