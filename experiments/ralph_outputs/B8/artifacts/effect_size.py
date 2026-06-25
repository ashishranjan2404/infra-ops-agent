#!/usr/bin/env python3
"""effect_size.py — Cohen's d and Cohen's h for SRE-Degrees pass@k result JSONs.

Task B8 (Ralph Loop). Computes standardized effect sizes for every claimed lift in
the project's pass@k result files, so a reviewer can see whether a headline like
"REx lifts pass@1 by +0.66" is a large effect or just noise-on-a-small-baseline.

We use the statistically appropriate measure per quantity:

  * Cohen's h  — for differences between two PROPORTIONS (binary pass@1 rates).
    h = |2*asin(sqrt(p1)) - 2*asin(sqrt(p2))|, sign kept as (treat - base).
    The arcsine (variance-stabilizing) transform is the standard way to size a
    proportion gap; a raw difference of probabilities is misleading near 0/1.
    Cohen's benchmarks: 0.2 small, 0.5 medium, 0.8 large.

  * Cohen's d  — for differences between two CONTINUOUS means (mean graded reward).
    d = (m1 - m2) / s_pooled, with pooled SD weighted by (n-1).
    Cohen's benchmarks: 0.2 small, 0.5 medium, 0.8 large.

The script is import-safe (pure functions) and has a CLI that ingests the real
result JSONs (rex/eval_pass_at_k.py output shape: by_condition[cond].overall with
n, passes, mean_reward, reward_std). It reports, for each model file, the effect
size of every condition lift relative to the zero_shot baseline.

Usage:
    python3 effect_size.py FILE.json [FILE.json ...] [--baseline zero_shot] [--json]
    python3 effect_size.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys


# ---------------------------------------------------------------------------
# Core effect-size functions (pure, unit-tested)
# ---------------------------------------------------------------------------
def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h for two proportions. Signed: positive when p1 > p2.

    h = phi(p1) - phi(p2), where phi(p) = 2*arcsin(sqrt(p)).
    """
    for p in (p1, p2):
        if not 0.0 <= p <= 1.0:
            raise ValueError(f"proportion out of [0,1]: {p}")
    phi1 = 2.0 * math.asin(math.sqrt(p1))
    phi2 = 2.0 * math.asin(math.sqrt(p2))
    return phi1 - phi2


def pooled_sd(s1: float, n1: int, s2: float, n2: int) -> float:
    """Pooled standard deviation (weighted by n-1). Requires n1+n2 > 2."""
    if n1 < 1 or n2 < 1:
        raise ValueError("group sizes must be >= 1")
    if n1 + n2 <= 2:
        raise ValueError("need n1 + n2 > 2 for pooled SD")
    num = (n1 - 1) * s1 * s1 + (n2 - 1) * s2 * s2
    return math.sqrt(num / (n1 + n2 - 2))


def cohens_d(m1: float, s1: float, n1: int, m2: float, s2: float, n2: int) -> float:
    """Cohen's d for two continuous groups. Signed: positive when m1 > m2."""
    sp = pooled_sd(s1, n1, s2, n2)
    if sp == 0.0:
        # No within-group variance anywhere; effect is degenerate.
        return math.inf if m1 != m2 else 0.0
    return (m1 - m2) / sp


def magnitude(es: float) -> str:
    """Cohen's qualitative label (works for both d and h; same thresholds)."""
    a = abs(es)
    if a < 0.2:
        return "negligible"
    if a < 0.5:
        return "small"
    if a < 0.8:
        return "medium"
    return "large"


# ---------------------------------------------------------------------------
# Result-JSON ingestion
# ---------------------------------------------------------------------------
def _overall(cond_block: dict) -> dict:
    """Extract the overall stats dict from a by_condition[cond] block."""
    return cond_block["overall"]


def effect_sizes_for_file(data: dict, baseline: str = "zero_shot") -> dict:
    """Compute all lifts vs `baseline` for one result file.

    Returns {model, baseline, lifts: [ {condition, ...proportion + reward effect sizes} ]}.
    """
    conds = data["by_condition"]
    if baseline not in conds:
        raise KeyError(f"baseline condition '{baseline}' not in file (have {list(conds)})")
    base = _overall(conds[baseline])
    bp = base["passes"] / base["n"]            # baseline pass@1 proportion
    bm, bs, bn = base["mean_reward"], base["reward_std"], base["n"]

    lifts = []
    for cond, block in conds.items():
        if cond == baseline:
            continue
        o = _overall(block)
        tp = o["passes"] / o["n"]
        h = cohens_h(tp, bp)
        d = cohens_d(o["mean_reward"], o["reward_std"], o["n"], bm, bs, bn)
        lifts.append({
            "condition": cond,
            "baseline": baseline,
            # proportion lift (pass@1)
            "pass1_treat": round(tp, 4),
            "pass1_base": round(bp, 4),
            "pass1_diff": round(tp - bp, 4),
            "cohens_h": round(h, 4),
            "h_magnitude": magnitude(h),
            # continuous lift (mean reward)
            "reward_treat": round(o["mean_reward"], 4),
            "reward_base": round(bm, 4),
            "reward_diff": round(o["mean_reward"] - bm, 4),
            "cohens_d": round(d, 4) if math.isfinite(d) else d,
            "d_magnitude": magnitude(d),
            "n_treat": o["n"],
            "n_base": bn,
        })
    return {"model": data.get("model", "?"), "label": data.get("label", ""),
            "baseline": baseline, "lifts": lifts}


# ---------------------------------------------------------------------------
# Self-test against known textbook values
# ---------------------------------------------------------------------------
def _selftest() -> int:
    ok = True

    def check(name, got, want, tol=1e-3):
        nonlocal ok
        good = abs(got - want) <= tol
        ok = ok and good
        print(f"  [{'PASS' if good else 'FAIL'}] {name}: got={got:.5f} want={want:.5f}")

    # Cohen's h known values --------------------------------------------------
    # phi(p)=2 asin(sqrt p). p=0.5 -> phi = 2*asin(0.7071)=2*0.785398=1.570796 (pi/2).
    # p=0.25 -> 2*asin(0.5)=2*0.523599=1.047198. h(.5,.25)=0.523599.
    check("cohens_h(0.5,0.25)", cohens_h(0.50, 0.25), 0.523599)
    # Symmetry / sign
    check("cohens_h(0.25,0.5) = -above", cohens_h(0.25, 0.50), -0.523599)
    # Equal proportions -> 0
    check("cohens_h(0.4,0.4)", cohens_h(0.40, 0.40), 0.0)
    # p1=1,p2=0 -> phi(1)=2*asin(1)=pi ; phi(0)=0 ; h=pi
    check("cohens_h(1,0)=pi", cohens_h(1.0, 0.0), math.pi)

    # Cohen's d known value ---------------------------------------------------
    # Two groups, equal n=2, means 5 and 7, each SD = 2 (so pooled SD = 2).
    # d = (7-5)/2 = 1.0
    check("cohens_d means 7 vs 5, sd 2", cohens_d(7, 2, 2, 5, 2, 2), 1.0)
    # Equal SD=1, means differ by 0.5, large n -> d=0.5 exactly (pooled sd=1)
    check("cohens_d 0.5 sep, sd1", cohens_d(0.5, 1.0, 50, 0.0, 1.0, 50), 0.5)

    # pooled_sd known value: s1=2,s2=2 -> 2
    check("pooled_sd(2,10,2,10)", pooled_sd(2, 10, 2, 10), 2.0)
    # pooled_sd(3,5,5,5): num=(4*9 + 4*25)/8 = (36+100)/8=17 -> sqrt=4.1231
    check("pooled_sd(3,5,5,5)", pooled_sd(3, 5, 5, 5), math.sqrt(17.0))

    # magnitude labels
    assert magnitude(0.1) == "negligible"
    assert magnitude(0.3) == "small"
    assert magnitude(0.6) == "medium"
    assert magnitude(1.2) == "large"
    print("  [PASS] magnitude labels")

    print("SELFTEST:", "ALL PASS" if ok else "FAILURES")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="*", help="pass@k result JSON files")
    ap.add_argument("--baseline", default="zero_shot",
                    help="baseline condition to measure lifts against (default zero_shot)")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    ap.add_argument("--selftest", action="store_true", help="run unit self-test and exit")
    args = ap.parse_args(argv)

    if args.selftest:
        return _selftest()

    if not args.files:
        ap.error("provide at least one result JSON file (or --selftest)")

    all_out = []
    for f in args.files:
        with open(f) as fh:
            data = json.load(fh)
        out = effect_sizes_for_file(data, baseline=args.baseline)
        out["file"] = f
        all_out.append(out)

    if args.json:
        print(json.dumps(all_out, indent=2))
        return 0

    for out in all_out:
        print(f"\n=== {out['model']}  ({out.get('label','')})  baseline={out['baseline']} ===")
        print(f"{'condition':<16} {'pass@1':>8} {'Δp':>8} {'h':>8} {'h-mag':<11} "
              f"{'reward':>8} {'Δr':>8} {'d':>8} {'d-mag':<11}")
        for L in out["lifts"]:
            d = L["cohens_d"]
            d_s = f"{d:>8.3f}" if isinstance(d, (int, float)) and math.isfinite(d) else f"{str(d):>8}"
            print(f"{L['condition']:<16} {L['pass1_treat']:>8.3f} {L['pass1_diff']:>+8.3f} "
                  f"{L['cohens_h']:>+8.3f} {L['h_magnitude']:<11} "
                  f"{L['reward_treat']:>8.3f} {L['reward_diff']:>+8.3f} {d_s} {L['d_magnitude']:<11}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
