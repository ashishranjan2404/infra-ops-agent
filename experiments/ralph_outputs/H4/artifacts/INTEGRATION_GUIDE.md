# exptrack integration guide

`exptrack.py` is a dependency-free tracking shim. It uses **W&B** (or **Trackio**,
a drop-in W&B-compatible logger) when installed/configured, otherwise it writes a
local **JSONL** file. Tracking is best-effort: `init/log/summary/finish` never raise,
so adding it cannot crash a run.

## API

```python
import exptrack
run = exptrack.init(project="sre-degrees", name="train-glm5p2",
                    config={"lr": 1e-5, "group": 6, "steps": 30})
run.log({"mean_reward": 0.41, "reward_std": 0.12, "loss": 1.3}, step=step)
run.summary({"best_reward": 0.62})
run.finish()
# or:  with exptrack.init(...) as run: ...
```

Backend is chosen by `EXPTRACK_BACKEND` (`auto|wandb|trackio|jsonl|none`, default
`auto`). `auto` -> wandb if importable and `WANDB_DISABLED` is unset, else trackio,
else jsonl. JSONL files land in `EXPTRACK_DIR` (default `./_runs/<run_id>.jsonl`).

To make it importable from the core loops, either copy `exptrack.py` next to the
loop, add its dir to `PYTHONPATH`, or vendor it into the repo (e.g. `experiments/`).
These snippets assume `import exptrack` resolves.

---

## Integration A — train loop (`opensre-traj/train_rft_v2.py`)

The loop already computes `mean_r`, `spread`, `loss` per step and appends a JSONL
line. Add a tracker alongside it (do NOT remove the existing local log). Patch below
is also saved as `train_rft_v2.exptrack.patch`.

```diff
@@ async def run(args) -> int:
     logf = args.out
     if logf:
         os.makedirs(os.path.dirname(logf) or ".", exist_ok=True)
+    # --- exptrack: W&B-or-JSONL run-level tracking (best-effort, never raises) ---
+    import exptrack
+    track = exptrack.init(project="sre-degrees-train",
+                          name=f"rft-{args.model}",
+                          config={"model": args.model, "group": args.group,
+                                  "steps": args.steps, "lr": args.lr,
+                                  "tasks": args.tasks, "env": ENV})

     for step in range(args.steps):
@@
         line = {"step": step, "mean_reward": round(mean_r, 4), "reward_std": round(spread, 4),
                 "n": len(batch), "rewards": [round(x, 3) for x in rewards],
                 "loss": getattr(res, "loss", None)}
+        track.log({"mean_reward": mean_r, "reward_std": spread,
+                   "loss": line["loss"], "n": len(batch)}, step=step)
         print(f"step {step:>3}  mean_reward={mean_r:.4f}  spread={spread:.3f}  n={len(batch)}  "
               f"loss={line['loss']}")
         if logf:
             with open(logf, "a") as fh:
                 fh.write(json.dumps(line) + "\n")

+    track.summary({"final_step": args.steps - 1})
+    track.finish()
     if args.smoke:
         print("SMOKE OK: rollouts -> reward (v2 grader) -> forward/backward -> logged.")
     return 0
```

## Integration B — eval loop (`rex/eval_pass_at_k.py`)

`run_eval()` builds a per-condition results dict and `main()` dumps it to
`experiments/results/*.json`. Track the headline scalars per condition so eval
sweeps land in the same dashboard as training.

```diff
@@ def main():
     os.makedirs(RESULTS, exist_ok=True)
+    import exptrack
+    track = exptrack.init(project="sre-degrees-eval",
+                          name=f"pass_at_k-{args.model}",
+                          config={"model": args.model, "per_family": args.per_family,
+                                  "seeds": args.seeds, "conditions": args.conditions})
@@ in the loop over conditions (each `out[cond]` holds pass@k + spread):
+        for i, (cond, res) in enumerate(out.items()):
+            track.log({f"{cond}.pass@1": res.get("pass@1"),
+                       f"{cond}.pass@5": res.get("pass@5"),
+                       f"{cond}.reward_spread": res.get("reward_spread")}, step=i)
     json.dump(out, open(path, "w"), indent=2)
+    track.summary({"results_file": path})
+    track.finish()
```

(Adjust the metric keys to whatever `out[cond]` actually contains in your branch;
exptrack coerces unknown/None values safely.)

---

## Why a shim (not raw `wandb.init`)

1. **No hard dependency** — the repo runs in envs without wandb installed (the
   current one). Raw `import wandb` would break those loops; the shim degrades to JSONL.
2. **Best-effort** — a bad API key / offline box / quota error must not abort a
   30-step GRPO run. Every shim method swallows backend errors.
3. **One call site** — train and eval log through the same 3-method API, so swapping
   wandb<->trackio<->jsonl is an env var, not a code change.
