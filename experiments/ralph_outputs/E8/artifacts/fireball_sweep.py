#!/usr/bin/env python3
"""
E8 — Fireball data-scaling sweep harness.

Question: how much Fireball-format SFT trajectory data is needed (1k? 10k? 50k)?

This module provides:
  1. A *reader* for the Fireball-format JSONL corpus (the
     `state_before -> fix -> state_after` records in
     opensre-traj/out/trajectories.jsonl), tolerant of the synthetic fixture
     shape below.
  2. A *stratified subsetter* that draws deterministic N-sized subsets,
     preserving the per-incident-family and per-difficulty distribution so a
     1k slice is not accidentally all easy / all one family.
  3. A *sweep driver* that, given a list of N values and a fit-callback (the
     thing that actually trains/evaluates on a subset), records (N, score) and
     emits a sweep manifest. The driver does NOT invent scores: if no fit
     callback is supplied it only emits the subset manifests + the power
     analysis, and marks the score column as BLOCKED.
  4. A *power-analysis* estimator: given a target detectable effect and an
     observed-per-record reward variance, estimate the N needed, and (if any
     real (N, score) points exist) fit a saturating learning curve
     score(N) = a - b * N**(-c) to estimate the knee.

Nothing here fabricates a scaling curve. Real curves require a real fit
callback (a trainer/evaluator), which is the documented blocker — see
07_test_results.md / 09_critique.md.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable, Iterable, Optional

# ----------------------------------------------------------------------------
# 1. Reader
# ----------------------------------------------------------------------------

# Keys that identify a Fireball-format record. We require an id + a family
# label + a trajectory body; difficulty is optional (defaults to 0).
ID_KEYS = ("trajectory_id", "id", "uid")
FAMILY_KEYS = ("incident", "failure_mode", "family", "scenario_id")
TRAJ_KEYS = ("trajectory", "steps", "messages")


@dataclass
class Record:
    rid: str
    family: str
    difficulty: int
    n_steps: int
    raw: dict = field(repr=False)

    @property
    def stratum(self) -> str:
        return f"{self.family}::d{self.difficulty}"


def _first(d: dict, keys) -> Optional[object]:
    for k in keys:
        if k in d and d[k] is not None:
            return d[k]
    return None


def parse_record(d: dict) -> Optional[Record]:
    """Coerce one JSON object into a Record, or None if it is not Fireball-shaped."""
    rid = _first(d, ID_KEYS)
    fam = _first(d, FAMILY_KEYS)
    traj = _first(d, TRAJ_KEYS)
    if rid is None or fam is None or traj is None:
        return None
    if not isinstance(traj, list):
        return None
    diff = d.get("difficulty", 0)
    try:
        diff = int(diff)
    except (TypeError, ValueError):
        diff = 0
    return Record(rid=str(rid), family=str(fam), difficulty=diff,
                  n_steps=len(traj), raw=d)


def read_corpus(path: str | os.PathLike) -> list[Record]:
    """Read a JSONL Fireball corpus. Skips blank lines; raises on malformed JSON."""
    recs: list[Record] = []
    seen_ids: set[str] = set()
    with open(path, "r") as f:
        for ln, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{ln}: bad JSON: {e}") from e
            r = parse_record(obj)
            if r is None:
                continue
            # de-dup on id (Fireball corpora are appended from many runs)
            if r.rid in seen_ids:
                continue
            seen_ids.add(r.rid)
            recs.append(r)
    return recs


def corpus_profile(recs: list[Record]) -> dict:
    fam = Counter(r.family for r in recs)
    diff = Counter(r.difficulty for r in recs)
    steps = [r.n_steps for r in recs]
    return {
        "n_records": len(recs),
        "n_families": len(fam),
        "per_family": dict(fam.most_common()),
        "per_difficulty": dict(sorted(diff.items())),
        "mean_steps": round(sum(steps) / len(steps), 2) if steps else 0.0,
    }


# ----------------------------------------------------------------------------
# 2. Stratified subsetter
# ----------------------------------------------------------------------------

def _seed_int(seed: str) -> int:
    return int(hashlib.sha256(seed.encode()).hexdigest()[:8], 16)


def stratified_subset(recs: list[Record], n: int, seed: str = "E8") -> list[Record]:
    """Deterministic stratified sample of size <= n.

    Preserves the family::difficulty distribution. If n >= len(recs), returns a
    shuffled copy of the whole corpus (you can't draw more than you have).
    Sampling is *nested deterministic*: subset(N1) is a near-subset of subset(N2)
    for N1 < N2 because each stratum is sorted by a stable per-record hash and we
    take a prefix — this lets a sweep reuse rollouts across N points.
    """
    if n <= 0:
        return []
    rng = random.Random(_seed_int(seed))
    by_stratum: dict[str, list[Record]] = defaultdict(list)
    for r in recs:
        by_stratum[r.stratum].append(r)
    # stable order within a stratum by hash(seed+rid)
    for s in by_stratum.values():
        s.sort(key=lambda r: hashlib.sha256(f"{seed}:{r.rid}".encode()).hexdigest())

    total = len(recs)
    if n >= total:
        out = list(recs)
        rng.shuffle(out)
        return out

    # largest-remainder apportionment of n across strata by their size
    quotas: dict[str, float] = {s: len(v) / total * n for s, v in by_stratum.items()}
    base = {s: int(math.floor(q)) for s, q in quotas.items()}
    remaining = n - sum(base.values())
    # hand out the leftover to the strata with the largest fractional part
    frac_order = sorted(quotas, key=lambda s: quotas[s] - base[s], reverse=True)
    for s in frac_order[:remaining]:
        base[s] += 1

    out: list[Record] = []
    for s, k in base.items():
        out.extend(by_stratum[s][:k])
    rng.shuffle(out)
    return out


# ----------------------------------------------------------------------------
# 3. Power analysis
# ----------------------------------------------------------------------------

def required_n_for_effect(delta: float, sd: float, alpha: float = 0.05,
                          power: float = 0.80) -> int:
    """Per-arm N of *eval rollouts* to detect a mean-reward difference `delta`
    between two policies (e.g. trained-on-N1 vs trained-on-N2), given per-rollout
    reward sd `sd`. NOTE: this is the EVAL measurement budget for a single sweep
    point, NOT the number of training trajectories (that headline is the blocked
    quantity). Normal approximation:
        n = 2 * ((z_alpha/2 + z_beta) * sd / delta)**2
    Returns the per-arm N (so a sweep comparing two data sizes needs ~2n rollouts).
    """
    if delta <= 0 or sd <= 0:
        raise ValueError("delta and sd must be > 0")
    # inverse-normal via Acklam approximation (no scipy dependency)
    z_alpha = _z(1 - alpha / 2)
    z_beta = _z(power)
    n = 2.0 * ((z_alpha + z_beta) * sd / delta) ** 2
    return int(math.ceil(n))


def _z(p: float) -> float:
    """Inverse standard-normal CDF (Acklam). Good to ~1e-9 over (0,1)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00,
         3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
           (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def fit_learning_curve(points: list[tuple[int, float]]) -> Optional[dict]:
    """Fit score(N) = a - b * N**(-c) by coarse grid search on (a,b,c).

    Returns None unless >=4 real (N, score) points are supplied. This is the
    guard that prevents fabricating a curve from too few / zero points.
    """
    pts = sorted(set(points))
    if len(pts) < 4:
        return None
    ns = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    ymax = max(ys)
    best = None
    for a in [ymax + i * 0.02 for i in range(0, 8)]:
        for b in [0.05 * i for i in range(1, 40)]:
            for c in [0.1 * i for i in range(1, 20)]:
                sse = 0.0
                for n, y in zip(ns, ys):
                    pred = a - b * (n ** (-c))
                    sse += (pred - y) ** 2
                if best is None or sse < best[0]:
                    best = (sse, a, b, c)
    sse, a, b, c = best
    # knee = N where we reach 95% of the asymptote a
    target = 0.95 * a
    knee = None
    if b > 0 and c > 0 and a > target:
        knee = (b / (a - target)) ** (1.0 / c)
    return {"a": round(a, 4), "b": round(b, 4), "c": round(c, 4),
            "sse": round(sse, 5), "asymptote": round(a, 4),
            "knee_N_95pct": int(math.ceil(knee)) if knee else None,
            "n_points": len(pts)}


# ----------------------------------------------------------------------------
# 4. Sweep driver
# ----------------------------------------------------------------------------

FitCallback = Callable[[list[Record], str], float]
# (subset, seed) -> score in [0,1]. The REAL trainer/evaluator. Optional.


def run_sweep(recs: list[Record], n_grid: list[int], seeds: list[str],
              fit: Optional[FitCallback] = None, out_dir: Optional[str] = None) -> dict:
    """Run the data-size sweep.

    For each N in n_grid and each seed, draw a stratified subset, write its
    manifest, and (if `fit` supplied) score it. With no `fit`, the score is
    None and the run is marked BLOCKED — we emit subsets + power analysis only.
    """
    out: dict = {"n_grid": n_grid, "seeds": seeds, "points": [], "blocked": fit is None}
    raw_points: list[tuple[int, float]] = []
    for n in n_grid:
        for seed in seeds:
            sub = stratified_subset(recs, n, seed=seed)
            prof = corpus_profile(sub)
            score = None
            if fit is not None:
                score = float(fit(sub, seed))
                raw_points.append((len(sub), score))
            entry = {"requested_N": n, "actual_N": len(sub), "seed": seed,
                     "score": score, "n_families": prof["n_families"],
                     "per_difficulty": prof["per_difficulty"]}
            out["points"].append(entry)
            if out_dir:
                Path(out_dir).mkdir(parents=True, exist_ok=True)
                mpath = Path(out_dir) / f"subset_N{n}_{seed}.manifest.json"
                with open(mpath, "w") as f:
                    json.dump({"requested_N": n, "actual_N": len(sub),
                               "seed": seed, "ids": [r.rid for r in sub],
                               "profile": prof}, f, indent=2)
                entry["manifest"] = str(mpath)
    out["learning_curve"] = fit_learning_curve(raw_points) if raw_points else None
    return out


# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------

def _default_corpus() -> str:
    here = Path(__file__).resolve()
    # walk up to repo root (/Users/mei/rl) then to the known corpus
    for parent in here.parents:
        cand = parent / "opensre-traj" / "out" / "trajectories.jsonl"
        if cand.exists():
            return str(cand)
    return ""


def main(argv=None):
    ap = argparse.ArgumentParser(description="Fireball data-scaling sweep")
    ap.add_argument("--corpus", default=_default_corpus(),
                    help="Fireball-format JSONL (default: repo trajectories.jsonl)")
    ap.add_argument("--n-grid", default="1000,5000,10000,25000,50000",
                    help="comma-separated requested N values")
    ap.add_argument("--seeds", default="s1,s2,s3", help="comma-separated seeds")
    ap.add_argument("--delta", type=float, default=0.05,
                    help="min detectable mean-reward effect for power analysis")
    ap.add_argument("--sd", type=float, default=0.22,
                    help="per-record reward sd (observed Claude half ~0.20-0.23)")
    ap.add_argument("--out-dir", default=None, help="write subset manifests here")
    ap.add_argument("--profile-only", action="store_true",
                    help="just print corpus profile + power analysis")
    args = ap.parse_args(argv)

    if not args.corpus or not Path(args.corpus).exists():
        raise SystemExit(f"corpus not found: {args.corpus!r}")
    recs = read_corpus(args.corpus)
    prof = corpus_profile(recs)
    n_grid = [int(x) for x in args.n_grid.split(",") if x.strip()]
    seeds = [s for s in args.seeds.split(",") if s.strip()]

    power = {
        "delta": args.delta, "sd": args.sd,
        "per_arm_N_alpha05_power80": required_n_for_effect(args.delta, args.sd),
    }

    if args.profile_only:
        print(json.dumps({"corpus": args.corpus, "profile": prof,
                          "power_analysis": power}, indent=2))
        return

    sweep = run_sweep(recs, n_grid, seeds, fit=None, out_dir=args.out_dir)
    print(json.dumps({"corpus": args.corpus, "profile": prof,
                      "power_analysis": power, "sweep": sweep}, indent=2))


if __name__ == "__main__":
    main()
