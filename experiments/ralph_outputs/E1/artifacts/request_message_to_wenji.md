# Draft message to Wenji — push the GRPO/Fireball branch

> **Subject: Push your GRPO/Fireball branch — it's the only thing blocking Claim 2**
>
> Hey Wenji — your post-hackathon GRPO run (Fireball-trained beats OpenSRE-only on cascades)
> is the sole blocker for paper Claim 2. It was never pushed, so nobody can replicate it. I
> checked the repo: **no `grpo`/`fireball`/`wenji` branch exists on `origin` or anywhere
> local**, and the Fireball corpus + your trained slug aren't in the tree. We already have
> the GRPO drivers, the deterministic judge, and the cascade eval — we just need your run.
>
> **Please push a branch `grpo-fireball` off current `main` with the minimal payload:**
> 1. **Fireball corpus** — the D&D trajectory data (`incidents.jsonl`); Git LFS or a link +
>    sha256 if it's big.
> 2. **Parity payload — pick ONE:** (a) your raw per-rollout trajectories so we re-grade with
>    our judge, OR (b) your grader source. A mean-reward log alone isn't enough to verify parity.
> 3. **Model provenance** — base model id + the fireball-trained HUD slug **and** a re-fork
>    recipe (slugs expire; we need to be able to recreate it).
> 4. **Run logs** — the Fireball run jsonl AND the OpenSRE-only baseline you compared to.
> 5. Drop an **`E1_MANIFEST.json`** at repo root (template below) so our verifier passes.
>
> **Exact recipe:**
> ```bash
> git fetch origin && git checkout -b grpo-fireball origin/main
> mkdir -p opensre-traj/fireball
> cp <your-corpus> opensre-traj/fireball/incidents.jsonl
> cp <your-rollouts> opensre-traj/fireball/rollouts.jsonl        # parity payload
> cp <your-run-log> opensre-traj/runs/train_fireball_qwen3-8b.jsonl
> #  -> write E1_MANIFEST.json (template in wenji_branch_manifest.md)
> git grep -nE 'HUD_API_KEY|sk-[A-Za-z0-9]{16}|AKIA|BEGIN .*PRIVATE KEY' || echo "no secrets ok"
> git add -A && git commit -m "GRPO Fireball run: corpus, rollouts, run logs, manifest"
> git push -u origin grpo-fireball   # then open a PR against main
> ```
>
> **If the HUD slug/job has expired** (it ran a while ago): just push the corpus + your
> driver + whatever logs survive, and a re-fork recipe (`hud models fork Qwen/Qwen3-8B …`) —
> we'll re-run. Don't let an expired slug stop the push.
>
> Once it lands I'll run our verifier
> (`experiments/ralph_outputs/E1/artifacts/verify_grpo_push.py`) and the cascade pass@1
> rerun. Targeting before Thursday so Claim 2 can move from "blocked" to "preliminary".
> Thanks!

---
*Context I cannot do myself: I'm a repo worker and cannot push a branch that lives only on
your machine / your HUD account. This is a genuine human-in-the-loop handoff — the package
above is everything needed to make the push one copy-paste.*
