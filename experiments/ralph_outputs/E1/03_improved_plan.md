# 03 — Improved Plan (post-grill)

## What changed vs 01_plan.md

### Accepted critiques
- **Two-gate model (DVO + PSRE, R3).** Split into a *push gate* (Wenji's responsibility, fast)
  and a *claim gate* (our responsibility, eval rerun). The integration checklist and request
  message now distinguish these so the push isn't blocked on full reproducibility metadata.
- **Reward parity is the crux (SMR, R2).** The request message now demands EITHER raw rollout
  trajectories OR Wenji's grader file — explicitly stating that a scalar `mean_reward` log
  (which is all our existing `runs/*.jsonl` contain) is **insufficient** to verify parity.
- **Slug fragility (RLE, R1/R2).** Manifest now asks for base model id + a re-fork/adapter
  export recipe, not only the ephemeral HUD slug.
- **Secrets + size hygiene (DVO).** Verifier now runs a secret scan and flags large binaries;
  checklist mandates LFS/external pointer for data & checkpoints and branch-off-current-`main`.

### Rejected critiques (and why)
- **PSRE R1 "no eval entrypoint = useless" → REJECTED** (per REV R2). We already own the eval
  entrypoint (`rex/eval_pass_at_k.py` + cascade scenarios). Requiring Wenji to also ship an
  eval harness inflates the ask and risks a second, diverging eval path. The branch ships the
  *policy + data provenance*; the eval stays ours.
- **SMR R1 "must push the exact grader" → PARTIALLY REJECTED** (per RLE R2). We don't *require*
  the grader IF raw trajectories are pushed (then we re-grade with the in-repo judge). Grader
  is one of two acceptable parity payloads, not mandatory.

## Refined deliverables
1. `grpo_inventory.json` — what GRPO machinery already exists (so the push is additive only).
2. `wenji_branch_manifest.md` — the minimal sufficient + nice-to-have payload, parity-aware.
3. `integration_checklist.md` — two-gate checklist (push gate / claim gate) + hygiene.
4. `request_message_to_wenji.md` — send-ready, with exact git recipe + the parity ask.
5. `verify_grpo_push.py` — read-only gate-1 verifier (presence, parse, secret scan, size),
   prints gate-2 next step (the cascade eval command). Runs today → reports BLOCKED.

## Unchanged
Objective, blocker statement, and the no-shared-core-edit constraint all stand.

## Success criteria (sharpened)
- Inventory is verified against `git` + filesystem (not asserted).
- Manifest's "minimal sufficient" list is parity-checkable.
- Verifier exits non-zero today with a clear "branch not pushed yet" message, and is
  structured to pass once the manifest lands.
