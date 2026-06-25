#!/usr/bin/env python3
"""mcnemar.py — paired McNemar significance test over ALL condition pairs.

The SRE-Degrees paper claims McNemar's paired test for comparing conditions but
never ran the full pairwise matrix. This is a standalone, dependency-free tool
(stdlib only) that:

  1. Ingests one or more pass@k result JSONs (the format emitted by
     rex.eval_pass_at_k / rex.run_ablation_v2 — see schema below).
  2. Extracts per-(incident, seed) binary pass/fail for every condition by
     thresholding the per-episode reward at the file's own `threshold`.
  3. Builds the McNemar 2x2 contingency table for EVERY unordered condition pair
     (C(k,2) pairs), overall and per incident family.
  4. Reports the exact two-sided binomial p-value, the continuity-corrected
     chi-square, and a Holm-Bonferroni-corrected significance flag across the
     family of pairwise tests (the paper claims significance but never corrected
     for multiple comparisons — this tool makes that honest).

Why McNemar (not a chi-square of independent proportions): the conditions are
evaluated on the SAME (incident, seed) pairs, so the samples are paired. McNemar
conditions on the discordant pairs only (one condition passes, the other fails),
which is exactly the right test for paired binary outcomes.

Input schema (per file), only the fields used here:
{
  "model": "<str>",
  "threshold": <float>,          # reward >= threshold counts as a PASS
  "seeds": <int>,
  "incidents_by_family": {"simple": [...], "cascade": [...], "novel": [...]},
  "by_condition": {
     "<cond>": {
        "per_incident_rewards": {"<incident>": [r_seed0, r_seed1, ...], ...}
     }, ...
  }
}

Usage:
  python3 mcnemar.py RESULT.json [RESULT2.json ...] [--out OUT.json] [--alpha 0.05]
  python3 mcnemar.py RESULT.json --threshold 0.8   # override file threshold

Output: a JSON report (and a printed table) with one block per input file.
Exit code 0 on success, 2 on usage/data error.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from itertools import combinations
from typing import Dict, List, Tuple


# ---------------------------------------------------------------------------
# core stats
# ---------------------------------------------------------------------------
def to_binary(reward: float, threshold: float) -> int:
    """A single episode is a PASS iff its reward meets the pass threshold."""
    return 1 if reward >= threshold else 0


def mcnemar_table(a_bits: List[int], b_bits: List[int]) -> Dict:
    """McNemar 2x2 + exact two-sided binomial p + continuity-corrected chi2.

    a_bits / b_bits are aligned binary pass vectors over the SAME paired episodes.
    b01 = A pass, B fail ; b10 = A fail, B pass (the discordant cells).
    """
    if len(a_bits) != len(b_bits):
        raise ValueError("aligned vectors must have equal length")
    both_pass = sum(1 for a, b in zip(a_bits, b_bits) if a and b)
    both_fail = sum(1 for a, b in zip(a_bits, b_bits) if not a and not b)
    b01 = sum(1 for a, b in zip(a_bits, b_bits) if a and not b)   # A>B
    b10 = sum(1 for a, b in zip(a_bits, b_bits) if not a and b)   # B>A
    n_disc = b01 + b10

    # exact two-sided binomial test: P(X <= min(b01,b10)) under Bin(n_disc, 0.5)
    if n_disc == 0:
        p_exact = 1.0
    else:
        k = min(b01, b10)
        tail = sum(math.comb(n_disc, i) for i in range(0, k + 1)) * (0.5 ** n_disc)
        p_exact = min(1.0, 2.0 * tail)

    # continuity-corrected chi-square (1 dof) — reported for the large-n reader
    chi2_cc = ((abs(b01 - b10) - 1) ** 2) / n_disc if n_disc > 0 else 0.0

    return {
        "n_pairs": len(a_bits),
        "both_pass": both_pass,
        "both_fail": both_fail,
        "a_pass_b_fail": b01,
        "a_fail_b_pass": b10,
        "n_discordant": n_disc,
        "p_exact": round(p_exact, 6),
        "chi2_cc": round(chi2_cc, 4),
    }


def holm_bonferroni(pairs: List[Tuple[str, float]], alpha: float) -> Dict[str, dict]:
    """Holm-Bonferroni step-down correction over a family of p-values.

    pairs: list of (label, p_raw). Returns {label: {p_raw, p_adj, significant}}.
    p_adj is the monotone-enforced Holm-adjusted p (comparable to alpha directly).
    """
    m = len(pairs)
    ordered = sorted(pairs, key=lambda kv: kv[1])
    out: Dict[str, dict] = {}
    prev_adj = 0.0
    still_rejecting = True
    for rank, (label, p) in enumerate(ordered):
        adj = min(1.0, (m - rank) * p)
        adj = max(adj, prev_adj)  # enforce monotonicity
        prev_adj = adj
        if not (p < alpha / (m - rank)):
            still_rejecting = False
        significant = still_rejecting
        out[label] = {
            "p_raw": round(p, 6),
            "p_holm": round(adj, 6),
            "significant_holm": significant,
        }
    return out


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------
def aligned_bits(data: dict, cond: str, incidents: List[str], threshold: float) -> List[int]:
    """Flatten per-incident reward lists into one incident-major, seed-ordered
    binary pass vector for `cond`, restricted to `incidents`. Order is identical
    across conditions because we iterate the same incident list and seed index."""
    per = data["by_condition"][cond]["per_incident_rewards"]
    out: List[int] = []
    for inc in incidents:
        rewards = per.get(inc)
        if rewards is None:
            raise KeyError(f"condition '{cond}' missing incident '{inc}'")
        out.extend(to_binary(r, threshold) for r in rewards)
    return out


def family_incidents(data: dict) -> Dict[str, List[str]]:
    fams = data.get("incidents_by_family", {})
    out = {fam: sorted(incs) for fam, incs in fams.items()}
    # "overall" = every incident actually present in per_incident_rewards,
    # so the tool still works on files without a family map.
    any_cond = next(iter(data["by_condition"]))
    all_inc = sorted(data["by_condition"][any_cond]["per_incident_rewards"].keys())
    out_full = {"overall": all_inc}
    out_full.update(out)
    return out_full


def analyze_file(data: dict, threshold_override: float | None, alpha: float) -> dict:
    threshold = threshold_override if threshold_override is not None else data["threshold"]
    conditions = sorted(data["by_condition"].keys())
    fam_map = family_incidents(data)

    report = {
        "model": data.get("model"),
        "label": data.get("label"),
        "threshold": threshold,
        "seeds": data.get("seeds"),
        "conditions": conditions,
        "n_condition_pairs": len(list(combinations(conditions, 2))),
        "alpha": alpha,
        "by_family": {},
    }

    for fam, incidents in fam_map.items():
        if not incidents:
            continue
        # cache aligned bit vectors per condition for this family
        bits = {c: aligned_bits(data, c, incidents, threshold) for c in conditions}
        pair_tables: Dict[str, dict] = {}
        raw_for_holm: List[Tuple[str, float]] = []
        for ca, cb in combinations(conditions, 2):
            key = f"{ca}__vs__{cb}"
            tbl = mcnemar_table(bits[ca], bits[cb])
            tbl["pass_rate_a"] = round(sum(bits[ca]) / len(bits[ca]), 4)
            tbl["pass_rate_b"] = round(sum(bits[cb]) / len(bits[cb]), 4)
            pair_tables[key] = tbl
            raw_for_holm.append((key, tbl["p_exact"]))
        holm = holm_bonferroni(raw_for_holm, alpha)
        for key, h in holm.items():
            pair_tables[key].update(h)
            pair_tables[key]["significant_raw"] = pair_tables[key]["p_exact"] < alpha
        report["by_family"][fam] = {
            "n_incidents": len(incidents),
            "n_pairs_per_test": len(incidents) * (data.get("seeds") or 0),
            "pairs": pair_tables,
        }
    return report


# ---------------------------------------------------------------------------
# pretty print
# ---------------------------------------------------------------------------
def print_report(rep: dict) -> None:
    print(f"\n{'='*92}")
    print(f"McNemar paired test — model={rep['model']} threshold={rep['threshold']} "
          f"seeds={rep['seeds']} | {rep['n_condition_pairs']} condition pairs, "
          f"Holm alpha={rep['alpha']}")
    print('=' * 92)
    for fam, blk in rep["by_family"].items():
        print(f"\n[{fam}]  n_incidents={blk['n_incidents']}  "
              f"paired episodes/test={blk['n_pairs_per_test']}")
        print(f"  {'pair':<40} {'b01':>4} {'b10':>4} {'disc':>5} "
              f"{'p_exact':>9} {'p_holm':>9}  sig")
        for key, t in blk["pairs"].items():
            star = "***" if t.get("significant_holm") else (
                "*" if t.get("significant_raw") else "")
            print(f"  {key:<40} {t['a_pass_b_fail']:>4} {t['a_fail_b_pass']:>4} "
                  f"{t['n_discordant']:>5} {t['p_exact']:>9.5f} "
                  f"{t['p_holm']:>9.5f}  {star}")
    print("\n  legend: b01=A-pass/B-fail  b10=A-fail/B-pass  "
          "***=Holm-significant  *=raw-significant-only")


# ---------------------------------------------------------------------------
# cli
# ---------------------------------------------------------------------------
def main(argv: List[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("results", nargs="+", help="pass@k result JSON file(s)")
    ap.add_argument("--out", default=None, help="write combined JSON report here")
    ap.add_argument("--alpha", type=float, default=0.05, help="significance level")
    ap.add_argument("--threshold", type=float, default=None,
                    help="override pass threshold (default: file's own)")
    args = ap.parse_args(argv)

    combined = {"alpha": args.alpha, "files": {}}
    for path in args.results:
        try:
            data = json.load(open(path))
        except (OSError, json.JSONDecodeError) as e:
            print(f"ERROR reading {path}: {e}", file=sys.stderr)
            return 2
        if "by_condition" not in data:
            print(f"ERROR: {path} has no 'by_condition' block", file=sys.stderr)
            return 2
        try:
            rep = analyze_file(data, args.threshold, args.alpha)
        except (KeyError, ValueError) as e:
            print(f"ERROR analyzing {path}: {e}", file=sys.stderr)
            return 2
        combined["files"][path] = rep
        print_report(rep)

    if args.out:
        with open(args.out, "w") as f:
            json.dump(combined, f, indent=2)
        print(f"\nwrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
