#!/usr/bin/env python3
"""D11 — Training-stability / seed-variance analyzer for the opensre RFT (GRPO) run.

Zero external deps (stdlib only). Decoupled from the trainer / HUD / numpy.

Two modes:
  * cross-config (default): each --logs file is an independent (model,config) run.
    Reports per-run curve stats + a CAVEATED cross-config spread. This is NOT seed
    variance (different model size / n / trainer version are confounds).
  * seed-group (--seed-group LABEL): ALL --logs files are seeds of ONE config.
    Reports a proper Student-t 95% CI on the per-seed final reward.

Per-step record schema (real opensre logs):
  {"step":int,"mean_reward":float,"n":int,"rewards":[float...],
   "reward_std":float(optional),"loss":float|null}

Usage:
  python3 seed_variance.py --logs a.jsonl b.jsonl --out-json report.json --out-md table.md
  python3 seed_variance.py --logs runs/seed_*.jsonl --seed-group qwen3-8b@1e-5 ...
"""
from __future__ import annotations

import argparse
import dataclasses
import datetime as _dt
import glob
import json
import math
import statistics as st
from dataclasses import dataclass

# 95% two-sided Student-t multipliers, df 1..30 (df>30 -> 1.96 normal approx).
_T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365,
        8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179, 13: 2.160, 14: 2.145,
        15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 21: 2.080,
        22: 2.074, 23: 2.069, 24: 2.064, 25: 2.060, 26: 2.056, 27: 2.052, 28: 2.048,
        29: 2.045, 30: 2.042}


def t_multiplier(df: int) -> float:
    if df <= 0:
        raise ValueError("df must be >= 1")
    return _T95.get(df, 1.96)


@dataclass
class RunStats:
    path: str
    n_steps: int
    group_n: int
    curve_mean: float
    curve_std: float          # whole-curve (incl. learning trend) — NOT stability
    plateau_mean: float       # mean of last-k mean_reward (final perf estimate)
    plateau_std: float        # std of last-k mean_reward (detrended stability)
    plateau_window: int
    within_step_spread_mean: float
    within_step_spread_min: float
    collapse_steps: list
    first_reward: float
    last_reward: float
    delta: float


@dataclass
class SeedCI:
    statistic: str
    n_seeds: int
    mean: float
    std: float
    sem: float
    t_mult: float
    ci_low: float
    ci_high: float
    per_seed: list


def load_run(path: str) -> list:
    recs = []
    with open(path) as fh:
        for line in fh:
            s = line.strip()
            if not s:
                continue
            try:
                rec = json.loads(s)
            except json.JSONDecodeError:
                continue
            if "step" not in rec or "mean_reward" not in rec:
                continue
            recs.append(rec)
    return recs


def per_step_spread(rec: dict) -> float:
    """Within-group reward spread for one step.

    Prefer the logged population std (v2 logs it); else recompute population std
    from rewards[] (we have the whole group, so population std is correct).
    """
    if isinstance(rec.get("reward_std"), (int, float)):
        return float(rec["reward_std"])
    rw = rec.get("rewards") or []
    if len(rw) < 2:
        return 0.0
    return st.pstdev(rw)


def run_stats(path: str, recs: list, last_k: int, collapse_thresh: float) -> RunStats:
    means = [float(r["mean_reward"]) for r in recs]
    n_steps = len(means)
    group_n = int(recs[0].get("n", len(recs[0].get("rewards", [])))) if recs else 0

    window = min(last_k, n_steps)
    plateau = means[-window:] if window > 0 else []
    plateau_std = st.pstdev(plateau) if window >= 2 else 0.0

    spreads = [per_step_spread(r) for r in recs]
    collapse = [int(recs[i]["step"]) for i, sp in enumerate(spreads) if sp < collapse_thresh]

    return RunStats(
        path=path,
        n_steps=n_steps,
        group_n=group_n,
        curve_mean=round(st.fmean(means), 4),
        curve_std=round(st.pstdev(means) if n_steps >= 2 else 0.0, 4),
        plateau_mean=round(st.fmean(plateau), 4) if plateau else 0.0,
        plateau_std=round(plateau_std, 4),
        plateau_window=window,
        within_step_spread_mean=round(st.fmean(spreads), 4) if spreads else 0.0,
        within_step_spread_min=round(min(spreads), 4) if spreads else 0.0,
        collapse_steps=collapse,
        first_reward=round(means[0], 4) if means else 0.0,
        last_reward=round(means[-1], 4) if means else 0.0,
        delta=round(means[-1] - means[0], 4) if means else 0.0,
    )


def seed_ci(per_seed_finals: list, statistic: str) -> SeedCI | None:
    s = len(per_seed_finals)
    if s < 2:
        return None
    mean = st.fmean(per_seed_finals)
    std = st.stdev(per_seed_finals)          # sample std (seeds are a sample)
    sem = std / math.sqrt(s)
    tm = t_multiplier(s - 1)
    half = tm * sem
    return SeedCI(
        statistic=statistic, n_seeds=s,
        mean=round(mean, 4), std=round(std, 4), sem=round(sem, 4), t_mult=tm,
        ci_low=round(mean - half, 4), ci_high=round(mean + half, 4),
        per_seed=[round(x, 4) for x in per_seed_finals],
    )


def build_report(log_paths: list, seed_group: str | None,
                 last_k: int, collapse_thresh: float) -> dict:
    runs = []
    for p in log_paths:
        recs = load_run(p)
        if recs:
            runs.append(run_stats(p, recs, last_k, collapse_thresh))

    report = {
        "generated_utc": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
        "last_k": last_k,
        "collapse_thresh": collapse_thresh,
        "mode": "seed-group" if seed_group else "cross-config",
        "seed_group": seed_group,
        "seed_variance_status": (
            "MEASURED" if seed_group else
            "NOT MEASURED — trainer (train_rft.py / train_rft_v2.py) lacks a --seed flag; "
            "no run log contains a seed field. See add_seed_patch.diff + run_multiseed.sh "
            "(blocked on HUD Tinker GPU backend)."
        ),
        "runs": [dataclasses.asdict(r) for r in runs],
        "seed_ci": None,
        "cross_config": None,
        "notes": [],
    }

    if seed_group:
        finals = [r.plateau_mean for r in runs]
        ci = seed_ci(finals, statistic=f"plateau_mean (last-{last_k} mean_reward per seed)")
        report["seed_ci"] = dataclasses.asdict(ci) if ci else None
        report["notes"].append(
            "Seed CI uses Student-t (df=S-1, 95%) on each seed's last-k mean_reward. "
            "Steps within a seed are autocorrelated; the CI is across seeds, not steps.")
    else:
        plats = [r.plateau_mean for r in runs]
        report["cross_config"] = {
            "configs": [r.path for r in runs],
            "plateau_means": plats,
            "min": round(min(plats), 4) if plats else None,
            "max": round(max(plats), 4) if plats else None,
            "spread_std_ddof1": round(st.stdev(plats), 4) if len(plats) >= 2 else None,
            "caveat": ("NOT seed variance. Confounds: (1) model size (8B vs 30B), "
                       "(2) rollouts/step n (24 vs 40), (3) trainer version (v1 vs v2). "
                       "No CI computed — these are different configs, not seeds of one config."),
        }
        report["notes"].append(
            "To get a real seed-variance CI: apply add_seed_patch.diff, run run_multiseed.sh "
            "(5 seeds, same config), then re-run with --seed-group.")

    # GRPO advantage-collapse diagnostic summary
    any_collapse = [r.path for r in runs if r.collapse_steps]
    if any_collapse:
        report["notes"].append(
            f"GRPO advantage-collapse warning: within-step spread < {collapse_thresh} at some "
            f"steps in: {any_collapse}. Collapsed groups give ~zero advantage / no gradient signal.")
    else:
        report["notes"].append(
            f"No within-step spread collapse (all steps >= {collapse_thresh}); GRPO advantage "
            "signal preserved throughout every run.")
    return report


def render_md(report: dict) -> str:
    L = []
    L.append("# Training Stability / Seed-Variance Report\n")
    L.append(f"- generated: `{report['generated_utc']}`")
    L.append(f"- mode: **{report['mode']}**   last_k={report['last_k']}   "
             f"collapse_thresh={report['collapse_thresh']}")
    L.append(f"- **seed_variance_status:** {report['seed_variance_status']}\n")
    L.append("## Per-run stats")
    L.append("| run | steps | group_n | plateau_mean | **plateau_std** (stability) | "
             "within-step spread (mean/min) | curve_std (incl. trend — NOT stability) | "
             "delta (last-first) | collapse steps |")
    L.append("|---|--:|--:|--:|--:|--:|--:|--:|--:|")
    for r in report["runs"]:
        L.append("| `{p}` | {ns} | {g} | {pm} | {ps} | {wm}/{wmin} | {cs} | {d} | {col} |".format(
            p=r["path"].split("/")[-1], ns=r["n_steps"], g=r["group_n"],
            pm=r["plateau_mean"], ps=r["plateau_std"],
            wm=r["within_step_spread_mean"], wmin=r["within_step_spread_min"],
            cs=r["curve_std"], d=r["delta"],
            col=len(r["collapse_steps"])))
    L.append("")
    if report.get("seed_ci"):
        c = report["seed_ci"]
        L.append("## Across-seed 95% CI")
        L.append(f"- statistic: {c['statistic']}")
        L.append(f"- seeds (S) = {c['n_seeds']}, per-seed = {c['per_seed']}")
        L.append(f"- **mean = {c['mean']} ± {round(c['t_mult']*c['sem'],4)}**  "
                 f"(std={c['std']}, sem={c['sem']}, t(df={c['n_seeds']-1})={c['t_mult']})")
        L.append(f"- **95% CI = [{c['ci_low']}, {c['ci_high']}]**\n")
    if report.get("cross_config"):
        cc = report["cross_config"]
        L.append("## Cross-config spread (CAVEATED — NOT seed variance)")
        L.append(f"- plateau_means = {cc['plateau_means']}")
        L.append(f"- min={cc['min']}  max={cc['max']}  std(ddof=1)={cc['spread_std_ddof1']}")
        L.append(f"- caveat: {cc['caveat']}\n")
    L.append("## Notes")
    for n in report["notes"]:
        L.append(f"- {n}")
    return "\n".join(L) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--logs", nargs="+", required=True, help="jsonl run logs (globs ok)")
    ap.add_argument("--last-k", type=int, default=5)
    ap.add_argument("--collapse-thresh", type=float, default=0.03)
    ap.add_argument("--seed-group", default=None,
                    help="if set, treat all logs as seeds of ONE config (enables seed CI)")
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--out-md", default=None)
    args = ap.parse_args()

    paths = []
    for g in args.logs:
        paths.extend(sorted(glob.glob(g)) or [g])
    report = build_report(paths, args.seed_group, args.last_k, args.collapse_thresh)

    if args.out_json:
        with open(args.out_json, "w") as fh:
            json.dump(report, fh, indent=2)
    if args.out_md:
        with open(args.out_md, "w") as fh:
            fh.write(render_md(report))
    print(render_md(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
