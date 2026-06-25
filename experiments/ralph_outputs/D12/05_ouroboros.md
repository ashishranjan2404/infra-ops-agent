# D12 — 05 Ouroboros (self-critique, 3 different engineers)

## Engineer 1 — Statistician
**Problem found:** The script computes per-group sigma by slicing `rewards` into chunks of 4
assuming **task-major ordering**. If `ts.run` interleaves tasks (round-robin), a "group of 4" would
mix scenarios and inflate sigma. I must verify the ordering assumption.
**Resolution:** Checked the baseline jsonl: within each step the 40 rewards cluster in blocks of 4
with near-identical values (e.g. `0.706,0.706,0.706,0.713`), which only happens if 4 consecutive
entries are the SAME task. Task-major ordering confirmed empirically. Also reported per-step
reward_std (0.183) separately so the reader sees both the cross-task and within-task spreads — the
within-task one (0.069) is the correct GRPO quantity. Documented the assumption in the docstring.

## Engineer 2 — RL trainer maintainer
**Problem found:** The SEM=sigma/sqrt(G) story describes the *baseline mean* error, but GRPO often
normalizes advantage by the within-group std too (`A = (r-mean)/std`). If so, the dominant effect of
larger G is a *less biased std estimate*, not just baseline-mean SEM. Over-claiming the SEM framing
is a real gap.
**Resolution:** Kept the SEM framing as the *leading* exact result (it's provider-agnostic and
always true), but the interpretation paragraph explicitly frames 4→8 as "cleaner advantage estimate"
(covers both mean and std). Did not assert which normalization HUD's `trainer.step` uses internally,
since that's not visible in the repo — honest scoping, no fabricated internal behavior.

## Engineer 3 — Reproducibility/DevOps reviewer
**Problem found:** `run_group8.sh` uses a relative `cd "$(dirname $0)/../../../../opensre-traj"`.
If the file is moved, the path breaks; and `source ~/.zshrc` may fail in CI without a profile.
Also `variance_analysis.py`'s DEFAULT_LOG is a relative `../../../../` chain — fragile.
**Resolution:** Wrapped `source ~/.zshrc` in `|| true` so a missing profile doesn't abort. Made
DEFAULT_LOG resolve via `os.path.dirname(__file__)` + `os.path.abspath`, and added a `--log`
override + an explicit "log not found" exit. The `cd` is acceptable because artifacts live at a
fixed depth under `experiments/ralph_outputs/D12/artifacts/`; documented the assumption.

## Final filtered spec
- Ordering assumption (task-major) is **verified against the real log** and documented, not assumed.
- Claim scoped to "cleaner advantage estimate"; no fabricated internal normalization behavior.
- Paths hardened (`|| true`, `__file__`-relative default, `--log` override, not-found guard).
