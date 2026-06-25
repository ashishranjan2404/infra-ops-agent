#!/usr/bin/env python3
"""J4 — MTTR improvement analysis harness (agent-assisted vs unassisted).

Estimates the effect of agent assistance on Mean-Time-To-Resolve (MTTR) for SRE
incidents, supporting BOTH experiment designs:

  * within-subjects (paired):  the SAME incident is resolved once unassisted and
    once agent-assisted (e.g. matched operators / replayed scenario). Analyzed
    with a log-paired t-test + Wilcoxon signed-rank, paired bootstrap CI on the
    geometric-mean ratio, plus per-pair speedup.

  * between-subjects (A/B):    DIFFERENT incidents/operators are randomized to
    arm=control (unassisted) vs arm=agent (assisted). Analyzed with a
    Welch t-test on log(MTTR) + Mann-Whitney U, two-sample bootstrap CI on the
    geometric-mean ratio.

WHY log-space: incident durations are strongly right-skewed (A9 labels span
27 min .. 4380 min, ~160x). Differences-of-means are dominated by a few
mega-incidents; the policy-relevant, scale-free effect is the MULTIPLICATIVE
speedup (ratio of geometric means), so we test on log(MTTR).

Primary endpoint:  speedup = GM(unassisted) / GM(assisted)  (>1 means faster).
  equivalently exp(mean(log t_unassisted) - mean(log t_assisted)).
Secondary:  median MTTR per arm, % incidents resolved within SLO budget,
  Cliff's delta (nonparametric effect size).

Stdlib + numpy/scipy only. scipy is optional: if absent, t-test / Wilcoxon /
Mann-Whitney fall back to a bootstrap/permutation p-value so the harness still
runs hermetically. No network, no shared-core imports.

Input: a "trials" file (CSV or JSON). One row per resolution attempt:
  incident_id, arm ("control"|"agent"), mttr_minutes (float>0),
  [pair_id]  (REQUIRED for within-subjects; links the two arms of one incident),
  [operator_id], [resolved (bool, default true)]

Usage:
  mttr_analysis.py --trials trials.csv --design within   --out report.json
  mttr_analysis.py --trials trials.csv --design between  --slo 120
  mttr_analysis.py --self-test          # run built-in unit checks, exit 0/1
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from dataclasses import dataclass, asdict, field
from typing import Optional

try:
    import numpy as np
except Exception:  # pragma: no cover - numpy is expected but degrade gracefully
    np = None

try:
    from scipy import stats as _scipy_stats
    _HAVE_SCIPY = True
except Exception:
    _scipy_stats = None
    _HAVE_SCIPY = False


# --------------------------------------------------------------------------- #
# data model
# --------------------------------------------------------------------------- #
@dataclass
class Trial:
    incident_id: str
    arm: str               # "control" (unassisted) | "agent" (assisted)
    mttr_minutes: float
    pair_id: Optional[str] = None
    operator_id: Optional[str] = None
    resolved: bool = True

    def validate(self) -> None:
        if self.arm not in ("control", "agent"):
            raise ValueError(f"arm must be control|agent, got {self.arm!r}")
        if not (self.mttr_minutes is not None and self.mttr_minutes > 0):
            raise ValueError(f"mttr_minutes must be >0, got {self.mttr_minutes!r}")


def _to_bool(v) -> bool:
    if isinstance(v, bool):
        return v
    return str(v).strip().lower() in ("1", "true", "yes", "y", "t")


def load_trials(path: str) -> list[Trial]:
    if path.endswith(".json"):
        with open(path) as f:
            raw = json.load(f)
        rows = raw["trials"] if isinstance(raw, dict) else raw
    else:
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
    trials: list[Trial] = []
    for r in rows:
        if r.get("mttr_minutes") in (None, "", "null"):
            continue  # skip unlabeled rows transparently
        t = Trial(
            incident_id=str(r["incident_id"]),
            arm=str(r["arm"]).strip().lower(),
            mttr_minutes=float(r["mttr_minutes"]),
            pair_id=(str(r["pair_id"]) if r.get("pair_id") not in (None, "", "null") else None),
            operator_id=(str(r["operator_id"]) if r.get("operator_id") not in (None, "", "null") else None),
            resolved=_to_bool(r.get("resolved", True)),
        )
        t.validate()
        trials.append(t)
    return trials


# --------------------------------------------------------------------------- #
# stats helpers (numpy-light; pure-python fallbacks where cheap)
# --------------------------------------------------------------------------- #
def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def _gmean(xs: list[float]) -> float:
    return math.exp(_mean([math.log(x) for x in xs]))


def _median(xs: list[float]) -> float:
    s = sorted(xs)
    n = len(s)
    m = n // 2
    return s[m] if n % 2 else (s[m - 1] + s[m]) / 2.0


def _bootstrap_ratio_ci(log_c: list[float], log_a: list[float], *, paired: bool,
                        n_boot: int, seed: int, alpha: float = 0.05):
    """Bootstrap CI on speedup = GM(control)/GM(agent) = exp(mean(log_c)-mean(log_a))."""
    rng = random.Random(seed)
    ratios = []
    nc, na = len(log_c), len(log_a)
    for _ in range(n_boot):
        if paired:
            idx = [rng.randrange(nc) for _ in range(nc)]
            bc = [log_c[i] for i in idx]
            ba = [log_a[i] for i in idx]   # same indices -> preserves pairing
        else:
            bc = [log_c[rng.randrange(nc)] for _ in range(nc)]
            ba = [log_a[rng.randrange(na)] for _ in range(na)]
        ratios.append(math.exp(_mean(bc) - _mean(ba)))
    ratios.sort()
    lo = ratios[int((alpha / 2) * n_boot)]
    hi = ratios[int((1 - alpha / 2) * n_boot) - 1]
    return lo, hi


def _perm_pvalue_diff(a: list[float], b: list[float], *, paired: bool,
                      n_perm: int, seed: int) -> float:
    """Two-sided permutation p-value for difference in means (used if no scipy)."""
    rng = random.Random(seed)
    obs = abs(_mean(a) - _mean(b))
    cnt = 0
    if paired:
        diffs = [ai - bi for ai, bi in zip(a, b)]
        for _ in range(n_perm):
            signed = [d if rng.random() < 0.5 else -d for d in diffs]
            if abs(_mean(signed)) >= obs - 1e-12:
                cnt += 1
    else:
        pool = a + b
        na = len(a)
        for _ in range(n_perm):
            rng.shuffle(pool)
            if abs(_mean(pool[:na]) - _mean(pool[na:])) >= obs - 1e-12:
                cnt += 1
    return (cnt + 1) / (n_perm + 1)


def _cliffs_delta(a: list[float], b: list[float]) -> float:
    """Nonparametric effect size in [-1,1]; P(a>b)-P(a<b). a=control,b=agent."""
    gt = lt = 0
    for x in a:
        for y in b:
            if x > y:
                gt += 1
            elif x < y:
                lt += 1
    n = len(a) * len(b)
    return (gt - lt) / n if n else 0.0


# --------------------------------------------------------------------------- #
# analysis
# --------------------------------------------------------------------------- #
@dataclass
class Result:
    design: str
    n_control: int
    n_agent: int
    n_pairs: Optional[int]
    gm_control_min: float
    gm_agent_min: float
    median_control_min: float
    median_agent_min: float
    speedup: float                 # GM(control)/GM(agent); >1 = agent faster
    speedup_ci95: list             # [lo, hi]
    pct_reduction: float           # (1 - 1/speedup)*100
    p_value: float
    test_name: str
    effect_size_cliffs_delta: float
    slo_minutes: Optional[float]
    pct_within_slo_control: Optional[float]
    pct_within_slo_agent: Optional[float]
    significant_at_05: bool
    notes: list = field(default_factory=list)


def analyze(trials: list[Trial], *, design: str, slo: Optional[float] = None,
            n_boot: int = 5000, seed: int = 0) -> Result:
    ctrl = [t for t in trials if t.arm == "control"]
    agent = [t for t in trials if t.arm == "agent"]
    if not ctrl or not agent:
        raise ValueError("need >=1 trial in each arm (control and agent)")

    notes: list[str] = []

    if design == "within":
        # join on pair_id; require both arms present
        by_pair_c = {t.pair_id: t for t in ctrl if t.pair_id}
        by_pair_a = {t.pair_id: t for t in agent if t.pair_id}
        pids = sorted(set(by_pair_c) & set(by_pair_a))
        if not pids:
            raise ValueError("within design requires pair_id linking control & agent")
        dropped = (len(by_pair_c) - len(pids)) + (len(by_pair_a) - len(pids))
        if dropped:
            notes.append(f"dropped {dropped} unpaired trial(s)")
        c_vals = [by_pair_c[p].mttr_minutes for p in pids]
        a_vals = [by_pair_a[p].mttr_minutes for p in pids]
        log_c = [math.log(v) for v in c_vals]
        log_a = [math.log(v) for v in a_vals]
        n_pairs = len(pids)

        if _HAVE_SCIPY and n_pairs >= 2:
            tt = _scipy_stats.ttest_rel(log_c, log_a)
            p = float(tt.pvalue)
            test_name = "paired t-test on log(MTTR)"
            try:
                w = _scipy_stats.wilcoxon(c_vals, a_vals)
                notes.append(f"Wilcoxon signed-rank p={float(w.pvalue):.4f}")
            except Exception as e:
                notes.append(f"Wilcoxon skipped: {e}")
        else:
            p = _perm_pvalue_diff(log_c, log_a, paired=True, n_perm=max(n_boot, 5000), seed=seed)
            test_name = "paired sign-flip permutation on log(MTTR)" + ("" if _HAVE_SCIPY else " (no scipy)")
        ci = _bootstrap_ratio_ci(log_c, log_a, paired=True, n_boot=n_boot, seed=seed)
    elif design == "between":
        c_vals = [t.mttr_minutes for t in ctrl]
        a_vals = [t.mttr_minutes for t in agent]
        log_c = [math.log(v) for v in c_vals]
        log_a = [math.log(v) for v in a_vals]
        n_pairs = None
        if _HAVE_SCIPY and len(log_c) >= 2 and len(log_a) >= 2:
            tt = _scipy_stats.ttest_ind(log_c, log_a, equal_var=False)  # Welch
            p = float(tt.pvalue)
            test_name = "Welch t-test on log(MTTR)"
            try:
                u = _scipy_stats.mannwhitneyu(c_vals, a_vals, alternative="two-sided")
                notes.append(f"Mann-Whitney U p={float(u.pvalue):.4f}")
            except Exception as e:
                notes.append(f"Mann-Whitney skipped: {e}")
        else:
            p = _perm_pvalue_diff(log_c, log_a, paired=False, n_perm=max(n_boot, 5000), seed=seed)
            test_name = "two-sample permutation on log(MTTR)" + ("" if _HAVE_SCIPY else " (no scipy)")
        ci = _bootstrap_ratio_ci(log_c, log_a, paired=False, n_boot=n_boot, seed=seed)
    else:
        raise ValueError(f"design must be within|between, got {design!r}")

    speedup = math.exp(_mean(log_c) - _mean(log_a))
    pct_red = (1.0 - 1.0 / speedup) * 100.0

    within_c = within_a = None
    if slo is not None:
        within_c = 100.0 * sum(1 for v in c_vals if v <= slo) / len(c_vals)
        within_a = 100.0 * sum(1 for v in a_vals if v <= slo) / len(a_vals)

    return Result(
        design=design,
        n_control=len(c_vals),
        n_agent=len(a_vals),
        n_pairs=n_pairs,
        gm_control_min=round(_gmean(c_vals), 2),
        gm_agent_min=round(_gmean(a_vals), 2),
        median_control_min=round(_median(c_vals), 2),
        median_agent_min=round(_median(a_vals), 2),
        speedup=round(speedup, 4),
        speedup_ci95=[round(ci[0], 4), round(ci[1], 4)],
        pct_reduction=round(pct_red, 2),
        p_value=round(p, 6),
        test_name=test_name,
        effect_size_cliffs_delta=round(_cliffs_delta(c_vals, a_vals), 4),
        slo_minutes=slo,
        pct_within_slo_control=(round(within_c, 1) if within_c is not None else None),
        pct_within_slo_agent=(round(within_a, 1) if within_a is not None else None),
        significant_at_05=bool(p < 0.05),
        notes=notes,
    )


# --------------------------------------------------------------------------- #
# power analysis (planning aid)
# --------------------------------------------------------------------------- #
def required_n_paired(expected_speedup: float, sd_log_diff: float,
                      power: float = 0.8, alpha: float = 0.05) -> int:
    """Approx n pairs for a paired t-test to detect a multiplicative speedup.
    effect d = ln(speedup)/sd_log_diff;  n ~= ((z_a/2 + z_b)/d)^2 + 1."""
    # inverse-normal via scipy if present, else a rational approximation
    if _HAVE_SCIPY:
        z_a = _scipy_stats.norm.ppf(1 - alpha / 2)
        z_b = _scipy_stats.norm.ppf(power)
    else:
        z_a, z_b = 1.959963985, 0.841621234  # alpha=.05 two-sided, power=.8
    d = abs(math.log(expected_speedup)) / sd_log_diff
    if d == 0:
        return 10 ** 9
    return int(math.ceil(((z_a + z_b) / d) ** 2)) + 1


# --------------------------------------------------------------------------- #
# self-test (hermetic; no files needed)
# --------------------------------------------------------------------------- #
def _self_test() -> int:
    ok = True

    def check(name, cond):
        nonlocal ok
        print(f"  [{'PASS' if cond else 'FAIL'}] {name}")
        ok = ok and cond

    # 1. gmean / median sanity
    check("gmean(1,10,100)==10", abs(_gmean([1, 10, 100]) - 10) < 1e-9)
    check("median([1,2,3,4])==2.5", _median([1, 2, 3, 4]) == 2.5)

    # 2. within-subjects: construct a known 2x speedup, agent always faster
    rng = random.Random(7)
    trials = []
    for i in range(40):
        base = math.exp(rng.gauss(math.log(120), 0.6))   # control MTTR
        assisted = base / 2.0 * math.exp(rng.gauss(0, 0.1))  # ~2x faster
        pid = f"p{i}"
        trials.append(Trial(f"inc{i}", "control", base, pair_id=pid))
        trials.append(Trial(f"inc{i}", "agent", assisted, pair_id=pid))
    r = analyze(trials, design="within", slo=120, seed=1)
    check("within speedup ~2 (1.6..2.5)", 1.6 < r.speedup < 2.5)
    check("within CI brackets speedup", r.speedup_ci95[0] <= r.speedup <= r.speedup_ci95[1])
    check("within significant", r.significant_at_05 and r.p_value < 0.05)
    check("within n_pairs==40", r.n_pairs == 40)
    check("within cliffs_delta>0 (control slower)", r.effect_size_cliffs_delta > 0)

    # 3. between-subjects: no real effect -> not significant, speedup ~1
    trials_null = []
    for i in range(60):
        v = math.exp(rng.gauss(math.log(100), 0.5))
        trials_null.append(Trial(f"c{i}", "control", v))
        v2 = math.exp(rng.gauss(math.log(100), 0.5))
        trials_null.append(Trial(f"a{i}", "agent", v2))
    rn = analyze(trials_null, design="between", seed=2)
    check("between null speedup ~1 (0.7..1.4)", 0.7 < rn.speedup < 1.4)
    check("between null CI brackets 1.0", rn.speedup_ci95[0] <= 1.0 <= rn.speedup_ci95[1])

    # 4. validation rejects bad input
    try:
        Trial("x", "bogus", 10).validate(); bad = False
    except ValueError:
        bad = True
    check("rejects bad arm", bad)
    try:
        Trial("x", "agent", -5).validate(); bad2 = False
    except ValueError:
        bad2 = True
    check("rejects nonpositive mttr", bad2)

    # 5. power analysis monotonicity
    n_small = required_n_paired(1.2, 0.5)
    n_big = required_n_paired(2.0, 0.5)
    check("power: bigger effect needs fewer pairs", n_big < n_small)

    print("ALL PASS" if ok else "SOME FAILED")
    return 0 if ok else 1


# --------------------------------------------------------------------------- #
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="J4 MTTR improvement analysis")
    ap.add_argument("--trials", help="CSV/JSON of resolution trials")
    ap.add_argument("--design", choices=["within", "between"], default="within")
    ap.add_argument("--slo", type=float, default=None, help="SLO budget (minutes)")
    ap.add_argument("--n-boot", type=int, default=5000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", help="write JSON report here")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()
    if not args.trials:
        ap.error("--trials required (or use --self-test)")

    trials = load_trials(args.trials)
    res = analyze(trials, design=args.design, slo=args.slo,
                  n_boot=args.n_boot, seed=args.seed)
    report = asdict(res)
    report["_meta"] = {"scipy": _HAVE_SCIPY, "n_trials_loaded": len(trials),
                       "source": os.path.basename(args.trials)}
    js = json.dumps(report, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(js + "\n")
    print(js)
    print(f"\nSpeedup {res.speedup}x ({res.pct_reduction}% MTTR reduction), "
          f"95% CI {res.speedup_ci95}, p={res.p_value} [{res.test_name}]",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
