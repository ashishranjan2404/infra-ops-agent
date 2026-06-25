# 09 — Honest critique

## What's weak / what a reviewer attacks
1. **Eval integration is a snippet, not a verified patch.** Unlike the train loop, I did not
   ship a `git apply --check`-validated patch for `rex/eval_pass_at_k.py`, because the exact
   keys in `out[cond]` (pass@1/pass@5/spread) vary by branch and I didn't want to ship a
   diff that won't apply. A reviewer can fairly say "you only half-integrated." Mitigation:
   the snippet is precise about call site and notes the keys are branch-dependent.
2. **The W&B path is not network-tested.** I verified `auto` *selects* wandb (0.27.2 present)
   and that `WandbRun` wraps `.init/.log/.finish`, but I did not run an actual `wandb.init`
   to a real project (no login / would create external state). So the wandb branch is
   structurally correct but not end-to-end proven here. The JSONL branch — the one we
   actually depend on in dep-free envs — IS fully proven.
3. **No automatic config capture.** By deliberate design (DOL's no-tendrils rule) the shim
   doesn't record git SHA / reward version unless the caller passes them. A reproducibility
   purist (AAAI) might want that captured automatically; I pushed it to the call site.
4. **Trackio untested.** Treated as wandb-compatible by interface; not installed here, so
   the trackio branch is selection-logic-only. If trackio's API diverges from `.init/.log/
   .finish`, `WandbRun` would need a shim — currently it would just swallow the error and log
   nothing (silent), which conflicts slightly with RLE's visibility wish.
5. **Patch is against an untracked file.** `opensre-traj/train_rft_v2.py` is currently
   untracked (`??`) in this branch, so the patch targets a file not yet committed; if it gets
   restructured before commit, the hunks could drift. Low risk given it applied cleanly now.

## What's genuinely solid
- The fallback (our real dependency) is fully tested, typed, and best-effort; it cannot
  crash a training run, which was the #1 hard requirement.
- One identical 3-method API across both loops; backend is an env var.
- The train patch is real and verified-applyable without touching core.

## Honest blocked/negative results
- None fabricated. The only un-proven path (live wandb upload) is honestly flagged above
  rather than faked.
