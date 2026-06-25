# 02 — Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **REV** (AAAI Reviewer),
**RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial takes

**SMR:** The task is coordination, but the *scientific* content is reward parity. If Wenji's
GRPO used a different reward than our in-repo deterministic judge (`rex/scoring.py` /
`hud_env_v2.py`), the "Fireball beats OpenSRE on cascades" result isn't comparable to
anything we run here. The push must include the exact grader, not just the checkpoint slug.

**PSRE:** From an incident-response framing, the only thing that matters for the paper is
whether the Fireball-trained policy actually resolves cascade/multi-hop incidents better.
A pushed branch with no eval entrypoint on our 19–20 cascade scenarios is useless. Demand
the eval command, not just training code.

**REV:** As a reviewer I will reject "one run, not pushed" outright (this is literally noted
in `PAPER_QUESTIONS.md` §4). The deliverable should make the result *reproducible by a third
party*: seed, model base, data hash, step count, and the run log. Without those, Claim 2
stays unsupported regardless of whether a branch appears.

**RLE:** Practically, the branch needs: the Fireball SFT/trajectory corpus
(`incidents.jsonl`), the GRPO driver (we already have `train_rft.py`/`train_rft_v2.py` shape),
the forked model slug, and the run jsonl. The HUD slug is the fragile part — a slug isn't a
checkpoint; if Wenji's fork is deleted on HUD, the branch is dead. Ask for the slug AND a
way to re-fork (base model + LoRA/head if exportable).

**DVO:** Mergeability and secrets. Wenji's branch finished "after the hackathon" on a
personal setup — high odds it carries `HUD_API_KEY`, absolute paths, or a 5GB run dir.
The checklist must enforce: branch off current `main`, no secrets, no giant binaries
(use Git LFS or an external pointer for checkpoints/data), green import.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**RLE → SMR (disagree):** SMR wants "the exact grader" pushed. I disagree that it must be
*pushed* — we ALREADY have the deterministic judge in-repo. Forcing Wenji to re-push a grader
risks a *fork* of the reward and two diverging judges. Better: Wenji pushes the run log +
the per-rollout rewards, and WE re-grade her trajectories with the in-repo judge. Parity is
verified, not duplicated.

**SMR → RLE (push back):** That only works if Wenji's branch contains the raw trajectories,
not just scalar rewards. If all we get is a `train_*.jsonl` of mean_reward (which is exactly
what our existing run logs are — see `runs/train_qwen3-8b_v2.jsonl`), we cannot re-grade.
So either she pushes trajectories OR she pushes her grader. "Just the log" is insufficient
for the parity claim. We disagree on what minimal is.

**REV → PSRE (disagree):** PSRE says "no eval entrypoint = useless." Too strong. We HAVE the
eval entrypoint (`rex/eval_pass_at_k.py` + the cascade scenarios). What's missing is the
*policy under test*. The branch's job is to deliver a runnable policy (slug/checkpoint) +
the data provenance; the eval is ours to run. Conflating the two inflates the ask and may
delay the push past Thursday.

**DVO → REV (disagree):** REV wants seed/hash/step-count "or the claim stays unsupported."
Agreed on rigor, but if we gate the *push* on full reproducibility metadata, Wenji may not
push at all before the deadline. Stage it: push the branch NOW (code+data+slug+log), file the
repro-metadata as a fast follow. An imperfect pushed branch beats a perfect unpushed one.

**PSRE → DVO (partial disagree):** DVO's "push now, metadata later" is fine for the branch but
NOT for the paper claim. For ops credibility I won't let Claim 2 into the paper on a branch
that can't be re-run. So: branch lands fast (DVO wins for the repo); claim stays "preliminary"
until the cascade eval reruns green (PSRE wins for the paper). These are two different gates.

## Round 3 — synthesis

Consensus reached:
1. **Two gates, not one.** *Push gate* (Wenji): code + Fireball data + model slug + run log,
   off current `main`, no secrets. *Claim gate* (us): re-run the cascade pass@1 eval with the
   in-repo judge and confirm Fireball > OpenSRE before the claim is anything but preliminary.
2. **Reward parity is the crux.** Minimal sufficient payload = EITHER raw rollout trajectories
   (so we re-grade with `rex/scoring.py`) OR Wenji's grader file. The request message must ask
   for one of these explicitly — a scalar mean-reward log alone is insufficient (SMR's point,
   conceded by RLE).
3. **Slug fragility is a real risk** (RLE): ask for base model + a re-fork recipe / exportable
   adapter, not just the ephemeral HUD slug.
4. **Secrets + size hygiene are blocking** (DVO): LFS/pointer for data & checkpoints, secret
   scan in the verifier.
5. **The verifier we ship** encodes gate-1 (push present + parseable + no secrets) and *prepares*
   gate-2 (points at the cascade eval command). It cannot itself prove the science — only that
   the branch is mergeable and complete.

This sharpened the deliverable from "ask Wenji to push" to "ask Wenji to push a *specific,
parity-checkable, secret-free manifest*, with a verifier that gates it."
