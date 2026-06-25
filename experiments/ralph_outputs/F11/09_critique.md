# F11 — 09 Critique (honest)

## What a reviewer will attack
1. **The headline number is never actually run here.** A skeptical AE chair notes that *Results
   Reproduced* — the badge that matters most — is unverified in this artifact bundle; I only ship
   the command. Mitigation in place (cost/credential honesty, exact command + comparison keys), but
   it remains a "trust the recipe" situation until someone spends the API budget. This is inherent
   to an LLM-in-the-loop benchmark, not a flaw I can fully close without credentials.

2. **Reproduction tolerance is defined but not parameterized in the paper here.** The appendix says
   "within the camera-ready Wilson CI," but that table isn't frozen in this repo yet. If the paper's
   reported `--per-family`/`--seeds` differ from the appendix's example commands, CI widths won't be
   comparable. A reviewer could call this underspecified. Fix would be to pin the exact paper config
   into the appendix once the camera-ready exists.

3. **Gateway model drift is a real reproducibility hole.** The proposer runs behind a model slug
   (`glm-5p2`, etc.) whose backing weights can change server-side. Even with a pinned commit, Tier B
   is not bit-reproducible across time. I disclose this honestly, but a strict AE chair may withhold
   *Reproduced* on the grounds that the substrate isn't fully archivable. The honest answer: only the
   *qualitative* ordering (REx > baseline on novel) is the durable claim.

4. **Availability is procedural, not done.** I describe the GitHub-release→Zenodo DOI path but do not
   mint a DOI (out of scope for a worker, and I shouldn't push/tag). So *Available* is "instructions,
   not artifact." A reviewer wanting a live DOI today would find only a plan.

5. **`floor_check` proves no *trivial* leak, not no leak.** It checks the empty plan and the first
   trap action. A cleverer reward-hack (partial-credit farming, e.g. the `trap_max=0.1` we observed)
   isn't a pass but shows the floor isn't zero. A determined adversary-evaluator could probe further;
   the appendix's integrity claim is "cheapest paths stay below threshold," which is true but modest.

## What's weak / missing
- No `Dockerfile` (deliberately rejected in 03, but some AE tracks expect one for Functional).
- No automated Tier-B *dry-run* that confirms the eval wiring without spending much (e.g. 1 incident,
  1 seed, a cheap model) — would have strengthened the "command actually works" claim. I verified the
  offline floor/judge paths and the argparse surface, but not a live single episode.
- Reproduction tolerance is qualitative pending the camera-ready numbers.

## Honest status
The *deliverable* (a real, grounded, self-checking artifact appendix) is complete and its offline
tier is demonstrably green. The *blocked* part is the paid, stochastic Tier-B reproduction, which is
correctly deferred rather than faked.
