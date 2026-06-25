#!/usr/bin/env python3
"""B12 — per-incident pass@k breakdown.

Ingests the pass@k result JSONs produced by the A1/A2 Ralph workers (the
`rex.eval_pass_at_k` schema: a dict with `model`, `threshold`, `seeds`,
`incidents_by_family`, and `by_condition[<cond>].per_incident_rewards`), and
emits a per-incident table:

    incident_id, family, source(model) -> {condition -> {pass@1, pass@k, n, passes}}

plus a `solvability` flag per incident:
    * "solvable"        — at least one condition reaches pass@1 == 1.0
                          (the incident is reliably solved by some policy)
    * "partially"       — best pass@1 across conditions is in (0, 1)
                          (sometimes solved, never reliably)
    * "unsolvable"      — NO condition ever passes a single sample (best pass@1 == 0)

The pass@k estimator is the standard unbiased Chen et al. (2021) estimator,
read from experiments/compute_pass_at_k.py when importable, with a local
fallback so the script is self-contained.

This script ONLY reads input JSONs and writes new files under its own output
dir — it does not touch any shared core file.

Usage:
    python3 per_incident_breakdown.py \
        --inputs <a1.json> <a2.json> ... \
        --out-json out/per_incident.json \
        --out-md   out/per_incident.md \
        [--k 2]      # pass@k k value (default: per-source max n)
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict

# ---- unbiased pass@k estimator (single source of truth + fallback) --------
try:
    REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    sys.path.insert(0, os.path.join(REPO, "experiments"))
    from compute_pass_at_k import pass_at_k as _pass_at_k  # type: ignore
except Exception:  # noqa: BLE001
    def _pass_at_k(n: int, c: int, k: int) -> float:
        """Prob >=1 of k samples passes given c/n passed (Chen et al. 2021)."""
        if n <= 0:
            return 0.0
        if k > n:
            k = n
        if c <= 0:
            return 0.0
        if n - c < k:
            return 1.0
        prod = 1.0
        for i in range(n - c + 1, n + 1):
            prod *= 1.0 - k / i
        return 1.0 - prod


def binary_pass(reward: float, threshold: float) -> int:
    return 1 if reward >= threshold else 0


# ---- ingest ---------------------------------------------------------------
def load_source(path: str) -> dict:
    with open(path) as f:
        d = json.load(f)
    if "by_condition" not in d or "incidents_by_family" not in d:
        raise ValueError(f"{path}: not a pass@k result JSON (missing keys)")
    return d


def incident_family_map(d: dict) -> dict:
    fam = {}
    for family, incs in d["incidents_by_family"].items():
        for inc in incs:
            fam[inc] = family
    return fam


# ---- per-incident aggregation ---------------------------------------------
def build_rows(sources: list, k_override) -> list:
    """One row per (source_model, incident). Each row holds per-condition
    pass@1/pass@k + a solvability flag."""
    rows = []
    for d in sources:
        model = d.get("model", "unknown")
        label = d.get("label", "")
        threshold = float(d.get("threshold", 0.8))
        fam = incident_family_map(d)
        conditions = list(d["by_condition"].keys())

        # collect the universe of incident ids seen in any condition
        inc_ids = set()
        for cond in conditions:
            inc_ids.update(d["by_condition"][cond].get("per_incident_rewards", {}).keys())

        for inc in sorted(inc_ids):
            per_cond = {}
            best_p1 = 0.0
            for cond in conditions:
                rewards = d["by_condition"][cond].get("per_incident_rewards", {}).get(inc)
                if rewards is None:
                    continue
                n = len(rewards)
                passes = sum(binary_pass(r, threshold) for r in rewards)
                p1 = passes / n if n else 0.0
                k = k_override if k_override else n
                per_cond[cond] = {
                    "n": n,
                    "passes": passes,
                    "pass@1": round(p1, 4),
                    f"pass@{k}": round(_pass_at_k(n, passes, k), 4),
                    "k": k,
                    "mean_reward": round(sum(rewards) / n, 4) if n else 0.0,
                }
                best_p1 = max(best_p1, p1)

            if best_p1 >= 1.0:
                solvability = "solvable"
            elif best_p1 > 0.0:
                solvability = "partially"
            else:
                solvability = "unsolvable"

            rows.append({
                "incident": inc,
                "family": fam.get(inc, "unknown"),
                "source_model": model,
                "source_label": label,
                "threshold": threshold,
                "best_pass@1": round(best_p1, 4),
                "solvability": solvability,
                "by_condition": per_cond,
            })
    return rows


def summarize(rows: list) -> dict:
    by_flag = defaultdict(list)
    by_family_flag = defaultdict(lambda: defaultdict(int))
    for r in rows:
        by_flag[r["solvability"]].append(f"{r['source_model']}:{r['incident']}")
        by_family_flag[r["family"]][r["solvability"]] += 1
    return {
        "n_rows": len(rows),
        "counts": {flag: len(v) for flag, v in by_flag.items()},
        "unsolvable": sorted(by_flag.get("unsolvable", [])),
        "partially": sorted(by_flag.get("partially", [])),
        "by_family": {fam: dict(d) for fam, d in by_family_flag.items()},
    }


# ---- markdown table -------------------------------------------------------
def render_md(rows: list, summary: dict) -> str:
    lines = []
    lines.append("# Per-incident pass@k breakdown\n")
    lines.append(f"Rows: {summary['n_rows']}  |  "
                 f"solvable={summary['counts'].get('solvable',0)}  "
                 f"partially={summary['counts'].get('partially',0)}  "
                 f"unsolvable={summary['counts'].get('unsolvable',0)}\n")

    # discover the union of conditions for stable column order
    cond_order = []
    for r in rows:
        for c in r["by_condition"]:
            if c not in cond_order:
                cond_order.append(c)

    header = ["incident", "family", "model", "flag", "best p@1"]
    for c in cond_order:
        header += [f"{c} p@1", f"{c} p@k"]
    lines.append("| " + " | ".join(header) + " |")
    lines.append("|" + "|".join(["---"] * len(header)) + "|")

    for r in rows:
        cells = [r["incident"], r["family"], r["source_model"],
                 r["solvability"], f"{r['best_pass@1']:.2f}"]
        for c in cond_order:
            pc = r["by_condition"].get(c)
            if pc is None:
                cells += ["-", "-"]
            else:
                k = pc["k"]
                cells += [f"{pc['pass@1']:.2f}", f"{pc[f'pass@{k}']:.2f}"]
        lines.append("| " + " | ".join(cells) + " |")

    lines.append("\n## Unsolvable incidents (no condition passes a single sample)\n")
    if summary["unsolvable"]:
        for x in summary["unsolvable"]:
            lines.append(f"- {x}")
    else:
        lines.append("- (none)")

    lines.append("\n## Partially-solvable (best pass@1 in (0,1) — never reliable)\n")
    if summary["partially"]:
        for x in summary["partially"]:
            lines.append(f"- {x}")
    else:
        lines.append("- (none)")

    lines.append("\n## By family\n")
    lines.append("| family | solvable | partially | unsolvable |")
    lines.append("|---|---|---|---|")
    for fam, d in sorted(summary["by_family"].items()):
        lines.append(f"| {fam} | {d.get('solvable',0)} | "
                     f"{d.get('partially',0)} | {d.get('unsolvable',0)} |")

    return "\n".join(lines) + "\n"


# ---- main -----------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Per-incident pass@k breakdown")
    ap.add_argument("--inputs", nargs="+", required=True,
                    help="pass@k result JSON files (A1/A2 schema)")
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--k", type=int, default=None,
                    help="pass@k k value (default: per-source sample count n)")
    args = ap.parse_args(argv)

    sources = []
    for p in args.inputs:
        try:
            sources.append(load_source(p))
            print(f"[ok] loaded {p}")
        except Exception as e:  # noqa: BLE001
            print(f"[skip] {p}: {e}", file=sys.stderr)

    if not sources:
        print("no valid input sources", file=sys.stderr)
        return 2

    rows = build_rows(sources, args.k)
    summary = summarize(rows)

    os.makedirs(os.path.dirname(os.path.abspath(args.out_json)) or ".", exist_ok=True)
    with open(args.out_json, "w") as f:
        json.dump({"summary": summary, "rows": rows}, f, indent=1)
    with open(args.out_md, "w") as f:
        f.write(render_md(rows, summary))

    print(f"[done] {summary['n_rows']} rows  "
          f"solvable={summary['counts'].get('solvable',0)} "
          f"partially={summary['counts'].get('partially',0)} "
          f"unsolvable={summary['counts'].get('unsolvable',0)}")
    print(f"  json -> {args.out_json}")
    print(f"  md   -> {args.out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
