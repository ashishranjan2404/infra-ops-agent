#!/usr/bin/env python3
"""
B14 cost_per_dollar.py — compute pass@1-per-dollar from available REx result JSONs.

Reads the real pass@k artifacts produced by rex/eval_pass_at_k.py (as stored under
experiments/ralph_outputs/A*/artifacts/), pulls per-condition pass@1, multiplies the
per-job estimated cost from cost_model.py by the number of incidents to get $/incident
under each condition, and emits a cost-efficiency table:

    cost_eff = pass@1  /  ($ per incident)        [pass-points per dollar]

Higher is better: how much pass@1 you buy per dollar of API spend.

Also reports $/100-incidents and the cost MULTIPLIER vs zero_shot, which is the
number a reviewer actually wants ("REx is 0.90 vs 0.23, but at Nx the cost").

Output:
  - cost_efficiency.json       (machine-readable)
  - cost_efficiency_table.md   (human-readable)

Run:  python3 cost_per_dollar.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import cost_model as cm  # noqa: E402

# Result JSONs to ingest. Each must have by_condition[*].overall.pass@1.
# Paths are relative to the repo root (…/rl). We resolve from HERE up to that root.
REPO = HERE.parents[3]  # B14/artifacts -> B14 -> ralph_outputs -> experiments -> rl
RESULT_FILES = [
    REPO / "experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json",
    REPO / "experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json",
]

# How much of the 1400-token output budget we assume a plan actually uses.
OUTPUT_UTIL = 0.6


def load_result(path: Path) -> dict | None:
    if not path.exists():
        print(f"  [skip] missing: {path}", file=sys.stderr)
        return None
    return json.loads(path.read_text())


def n_incidents(res: dict) -> int:
    n = res.get("n_incidents")
    if n:
        return int(n)
    fam = res.get("incidents_by_family", {})
    total = sum(len(v) for v in fam.values())
    return total or 0


def rows_for_result(res: dict) -> list[dict]:
    model = res["model"]
    n_inc = n_incidents(res)
    by_cond = res.get("by_condition", {})
    rows = []
    base_cost_per_inc = None  # zero_shot cost per incident, for the multiplier column
    # First pass: compute zero_shot per-incident cost for the multiplier baseline.
    if "zero_shot" in by_cond:
        jc0 = cm.estimate_job_cost(model, "zero_shot", output_token_utilization=OUTPUT_UTIL)
        base_cost_per_inc = jc0.usd  # per incident == per job (one seed of cost is representative)

    for cond, cd in by_cond.items():
        ov = cd.get("overall", {})
        p1 = ov.get("pass@1")
        if p1 is None:
            continue
        jc = cm.estimate_job_cost(model, cond, output_token_utilization=OUTPUT_UTIL)
        cost_per_inc = jc.usd                      # $ to run one incident under this condition
        cost_per_100 = cost_per_inc * 100.0
        # pass@1 per dollar of incident spend (pass-points per $; pass@1 is in [0,1]).
        cost_eff = (p1 / cost_per_inc) if cost_per_inc > 0 else float("inf")
        mult = (cost_per_inc / base_cost_per_inc) if base_cost_per_inc else None
        rows.append({
            "model": model,
            "condition": cond,
            "n_incidents": n_inc,
            "pass@1": round(p1, 4),
            "proposer_calls_per_job": jc.proposer_calls,
            "est_input_tokens_per_job": jc.input_tokens,
            "est_output_tokens_per_job": jc.output_tokens,
            "price_assumed": jc.price_assumed,
            "usd_per_incident": round(cost_per_inc, 6),
            "usd_per_100_incidents": round(cost_per_100, 4),
            "cost_mult_vs_zero_shot": round(mult, 2) if mult is not None else None,
            "pass@1_per_dollar": round(cost_eff, 2),
        })
    return rows


def main() -> int:
    all_rows: list[dict] = []
    sources: list[str] = []
    print("Ingesting result JSONs:")
    for path in RESULT_FILES:
        res = load_result(path)
        if res is None:
            continue
        sources.append(str(path.relative_to(REPO)))
        print(f"  [ok]  {path.relative_to(REPO)}  model={res.get('model')}  "
              f"n_incidents={n_incidents(res)}")
        all_rows.extend(rows_for_result(res))

    if not all_rows:
        print("No rows produced — no result JSONs found.", file=sys.stderr)
        return 1

    out = {
        "metric": "pass@1 per dollar of estimated API spend",
        "definition": "pass@1 / (estimated USD per incident under the condition)",
        "cost_basis": "ESTIMATED (tokens not logged); see cost_model.py for prices + call shape",
        "output_token_utilization_assumed": OUTPUT_UTIL,
        "sources": sources,
        "price_table": {
            m: {"in_per_m": p.in_per_m, "out_per_m": p.out_per_m,
                "assumed": p.assumed, "note": p.note}
            for m, p in cm.PRICES.items()
        },
        "proposer_calls_per_condition": cm.PROPOSER_CALLS,
        "rows": all_rows,
    }
    (HERE / "cost_efficiency.json").write_text(json.dumps(out, indent=2))

    # ---- markdown table ----
    lines = []
    lines.append("# B14 — Cost-Efficiency Table (pass@1 per dollar)\n")
    lines.append("Metric: **pass@1 / (estimated USD per incident)** — higher = more pass@1 "
                 "bought per dollar.\n")
    lines.append(f"Cost basis: **ESTIMATED** (tokens are not logged in the result JSONs). "
                 f"Output-token utilization assumed at {OUTPUT_UTIL:.0%} of the 1400-token "
                 f"`max_tokens` budget. Claude prices are real; gateway/Fireworks slugs use "
                 f"documented assumptions (see `price_assumed`).\n")
    hdr = ("| model | condition | pass@1 | calls/job | $/incident | $/100 inc | "
           "cost x vs zero_shot | pass@1 per $ | price assumed |")
    sep = "|" + "---|" * 9
    lines.append(hdr)
    lines.append(sep)
    for r in all_rows:
        lines.append(
            f"| {r['model']} | {r['condition']} | {r['pass@1']:.4f} | "
            f"{r['proposer_calls_per_job']:g} | ${r['usd_per_incident']:.6f} | "
            f"${r['usd_per_100_incidents']:.4f} | "
            f"{r['cost_mult_vs_zero_shot'] if r['cost_mult_vs_zero_shot'] is not None else '-'} | "
            f"{r['pass@1_per_dollar']:.2f} | {r['price_assumed']} |"
        )
    lines.append("")
    # per-model "best operating point by cost-efficiency"
    lines.append("## Most cost-efficient operating point per model\n")
    lines.append("| model | best condition (by pass@1 per $) | pass@1 | pass@1 per $ |")
    lines.append("|---|---|---|---|")
    by_model: dict[str, list[dict]] = {}
    for r in all_rows:
        by_model.setdefault(r["model"], []).append(r)
    for model, rs in by_model.items():
        best = max(rs, key=lambda x: x["pass@1_per_dollar"])
        lines.append(f"| {model} | {best['condition']} | {best['pass@1']:.4f} | "
                     f"{best['pass@1_per_dollar']:.2f} |")
    lines.append("")
    (HERE / "cost_efficiency_table.md").write_text("\n".join(lines))

    print("\nWrote:")
    print(f"  {(HERE/'cost_efficiency.json').relative_to(REPO)}")
    print(f"  {(HERE/'cost_efficiency_table.md').relative_to(REPO)}")
    print(f"\n{len(all_rows)} rows across {len(by_model)} model(s).")
    # echo the table to stdout too
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
