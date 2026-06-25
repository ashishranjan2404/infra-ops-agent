# GRPO Branch — Merge / Integration Checklist (two gates)

## GATE 1 — Push gate (Wenji's responsibility; fast, before Thursday)
- [ ] Branch created **off current `origin/main`** (not a stale hackathon base). Name: `grpo-fireball`.
- [ ] Contains the **minimal sufficient payload** (see `wenji_branch_manifest.md`):
      Fireball corpus, parity payload (trajectories OR grader), model provenance, run log.
- [ ] `E1_MANIFEST.json` added at repo root (so `verify_grpo_push.py` can check it).
- [ ] **No secrets**: no `HUD_API_KEY`, `sk-…`, AWS keys, private keys committed.
      (`git grep -nE 'HUD_API_KEY|sk-[A-Za-z0-9]{16}|AKIA|BEGIN .*PRIVATE KEY'` returns nothing.)
- [ ] **No fat raw binaries**: checkpoints / >25 MB data via Git LFS or external pointer.
- [ ] Does **not** modify shared core (`rex/*.py`, `sim/*.py`, `agent/*.py`) — additive only.
      If a reward change is needed, document it; don't fork `rex/scoring.py`.
- [ ] `python3 -m py_compile` clean on any added `.py`.
- [ ] Pushed: `git push -u origin grpo-fireball`, PR opened against `main`.
- [ ] `python3 experiments/ralph_outputs/E1/artifacts/verify_grpo_push.py` → exit 0.

## GATE 2 — Claim gate (our responsibility; after the push)
- [ ] Re-grade Wenji's rollouts with the in-repo deterministic judge (`rex/scoring.py`);
      assert `|our_reward − her_reward| < 1e-3` per rollout (reward parity).
- [ ] Run cascade eval: `python3 -m rex.eval_pass_at_k` for 3 policies
      (fireball-trained / opensre-trained / zero-shot), pass@1 by incident family.
- [ ] Confirm Fireball > OpenSRE-only on cascades by a meaningful margin (target ≥15pp pass@1,
      per `PAPER_QUESTIONS.md`), and note the simple-incident regression Wenji reported.
- [ ] Until gate-2 is green, Claim 2 stays labeled **preliminary** in the paper.

## Reviewer sign-off
- [ ] Reproducibility metadata present (seed/steps/lr/group/data-sha) — fast-follow OK for push,
      required before the claim ships.
- [ ] Co-author sign-off (Ashish, Wenji, Sylvie) per `NEXT_100_TASKS.md` F10.
