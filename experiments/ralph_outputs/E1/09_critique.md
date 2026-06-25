# 09 — Honest Critique

## The core limitation (unavoidable)
The task is **fundamentally blocked on a human action I cannot perform**: pushing a branch that
exists only on Wenji's machine/HUD account. No amount of repo work changes that. Everything here
is the *preparation* for the push, not the push. A skeptic is right to say "Claim 2 is still
blocked" — it is. What I produced reduces the human's effort to a single copy-paste and makes
the result verifiable, but it does not deliver the GRPO run.

## What a reviewer would attack
1. **Speculative manifest.** I specify what Wenji's branch *should* contain, inferred from
   meeting notes + the existing v1/v2 driver shapes. I have not seen her actual branch; the real
   layout may differ (different reward, different data format). Mitigation: the verifier is
   filename-agnostic via `E1_MANIFEST.json` and the parity ask is "trajectories OR grader" — but
   if her run used a reward incompatible with `rex/scoring.py`, parity may simply fail and the
   claim needs a re-run, not a re-grade. I flagged this but cannot resolve it pre-push.
2. **Verifier proves mergeability, not science.** Gate-1 passing means "complete & secret-free",
   NOT "Fireball beats OpenSRE". Easy to over-read a green check. I labeled this explicitly, but
   the risk of false confidence is real.
3. **Expired-artifact tail risk.** If the HUD slug/job has expired, even Wenji can't "just push";
   it becomes a re-run. I added a fallback path, but that fallback is itself a multi-hour GPU job
   I can't gate or guarantee.
4. **Single-run claim.** Even once pushed, `PAPER_QUESTIONS.md` notes it's one run. One pushed
   run is still N=1; the checklist marks the claim "preliminary" but doesn't fix statistical
   power. That's correct but unsatisfying for AAAI.

## What's weak
- The 15pp pass@1 target and ε=1e-3 parity tolerance are reasonable but somewhat arbitrary —
  pulled from `PAPER_QUESTIONS.md` and conventional float tolerance, not from a power analysis.
- size_scan's 25 MB threshold is a heuristic, not derived.

## What's genuinely solid
- The factual claim "no GRPO/Fireball branch exists on origin or locally" is verified, not
  assumed, and is the crux the whole paper-blocker hinges on.
- The verifier is real, stdlib-only, read-only, and demonstrably correct across 3 scenarios.
- The package is honestly scoped: it never fabricates a Fireball result.

## Bottom line
Status = **completed deliverable, downstream still blocked.** I produced everything a worker can
produce; the remaining step is irreducibly Wenji's.
