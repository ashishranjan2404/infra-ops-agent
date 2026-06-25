#!/usr/bin/env python3
"""B15 — compare our pass@1 (A1/A2 artifacts) against SREGym reported numbers.

Pure stdlib. Reads:
  - our A1 full-42 pass@k JSON   (glm-5p2)
  - our A2 ablation pass@k JSON  (deepseek-v4-pro)
  - a checked-in sregym_reported.json (numbers cited from paper + leaderboard)
Writes a distilled our_pass_at_1.json and a Markdown comparison table.

IMPORTANT (honesty): the two benchmarks are NOT equivalent. This script only
displays numbers side by side; the non-equivalence caveats live in
comparison_report.md and must be read with the table.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

CONDITIONS = ["zero_shot", "best_of_n", "retry_realistic", "rex_no_oracle", "rex"]
# Which of our conditions are a fair-ish analogue to a single-attempt scaffolded agent.
SINGLE_RUNISH = {"zero_shot", "best_of_n", "retry_realistic", "rex_no_oracle"}
REGIME = {
    "zero_shot": "single-shot (1 plan)",
    "best_of_n": "single-run-ish (best of N samples)",
    "retry_realistic": "single-run-ish (self retry)",
    "rex_no_oracle": "single-run-ish (tree, no oracle)",
    "rex": "MULTI-ATTEMPT + ORACLE (no SREGym counterpart)",
}


def _get(d, *keys, default=None):
    for k in keys:
        if isinstance(d, dict) and k in d and d[k] is not None:
            return d[k]
    return default


def fmt_pct(x):
    if x is None:
        return "—"
    return f"{x * 100:.1f}%"


def _cond_block(by_condition, cond, family):
    """Return {'p1','ci','n'} for a condition/family, tolerant of key spellings."""
    c = by_condition.get(cond)
    if not c:
        return None
    if family == "overall":
        fam = c.get("overall")
    else:
        # per-family splits are nested under by_family in A1's schema
        fam = (c.get("by_family") or {}).get(family) or c.get(family)
    if not fam:
        return None
    return {
        "p1": _get(fam, "pass@1", "p1"),
        "ci": _get(fam, "ci95", "ci"),
        "n": fam.get("n"),
    }


def load_our(a1_path, a2_path):
    a1 = json.loads(Path(a1_path).read_text())
    a2 = json.loads(Path(a2_path).read_text())
    a1bc = a1.get("by_condition", a1)
    a2bc = a2.get("by_condition", a2)
    out = {
        "source_runs": {
            "A1": {"file": str(a1_path), "model": a1.get("model"),
                   "n_incidents": sum(len(v) for v in a1.get("incidents_by_family", {}).values()) or None,
                   "seeds": a1.get("seeds")},
            "A2": {"file": str(a2_path), "model": a2.get("model"),
                   "n_incidents": a2.get("n_incidents"), "seeds": a2.get("seeds")},
        },
        "by_run": {"A1": {}, "A2": {}},
    }
    for cond in CONDITIONS:
        # A1 has per-family splits; record overall + families.
        a1c = {}
        for fam in ("overall", "simple", "cascade", "novel"):
            blk = _cond_block(a1bc, cond, fam)
            if blk:
                a1c[fam] = blk
        if a1c:
            out["by_run"]["A1"][cond] = a1c
        # A2: overall only (ablation; per-family optional / absent).
        blk2 = _cond_block(a2bc, cond, "overall")
        if blk2:
            out["by_run"]["A2"][cond] = {"overall": blk2}
    return out


def load_sregym(path):
    return json.loads(Path(path).read_text())


def _e2e_band(sregym, noise=False):
    vals = [r["e2e"] for r in sregym["leaderboard"] if r["noise"] == noise]
    return (min(vals), max(vals))


def render_table(our, sregym):
    lo, hi = _e2e_band(sregym, noise=False)
    nlo, nhi = _e2e_band(sregym, noise=True)
    a1 = our["by_run"]["A1"]
    a2 = our["by_run"]["A2"]
    L = []
    L.append("## Table 1 — Headline cross-benchmark (overall pass@1)\n")
    L.append("Our pass@1 = fraction of (incident x seed) where graded reward >= 0.8 "
             "(SLO restored + root cleared + no collateral). SREGym E2E = correct diagnosis "
             "AND mitigation, oracle-verified, single attempt/run (== pass@1 semantics).\n")
    L.append("| Our condition | A1 pass@1 (glm-5p2, n=42) | A2 pass@1 (deepseek-v4-pro, n=30) | Attempt regime |")
    L.append("|---|---|---|---|")
    for cond in CONDITIONS:
        p1a = fmt_pct(_get(a1.get(cond, {}).get("overall", {}), "p1"))
        p1b = fmt_pct(_get(a2.get(cond, {}).get("overall", {}), "p1"))
        L.append(f"| `{cond}` | {p1a} | {p1b} | {REGIME[cond]} |")
    L.append("")
    L.append("| Reference: SREGym (90 live tasks, single attempt/run) | E2E success |")
    L.append("|---|---|")
    L.append(f"| Range across agents, **no noise** | {fmt_pct(lo)} – {fmt_pct(hi)} |")
    L.append(f"| Range across agents, **with noise** | {fmt_pct(nlo)} – {fmt_pct(nhi)} |")
    L.append(f"| Best single entry (Claude Code, Sonnet 4.6, no noise) | {fmt_pct(hi)} |")
    L.append("")
    L.append("> **Caption:** \"E2E range\" is the spread across leaderboard agents, NOT a "
             "confidence interval. Our `rex` row (multi-attempt + oracle) has **no SREGym "
             "counterpart** — SREGym allows one attempt per run — and must not be read as "
             "\"beating\" SREGym. The fair single-attempt comparators are the "
             "`best_of_n`/`rex_no_oracle` band.\n")

    # Table 2 — loose family<->partition analogy
    rep = "Claude Code::Claude Sonnet 4.6::no_noise"
    pb = sregym["partition_breakdown"][rep]
    L.append("## Table 2 — LOOSE ANALOGY (not a validated mapping): family ↔ partition\n")
    L.append("Mapping simple↔Ported, cascade↔Similar, novel↔New is an **unvalidated analogy**; "
             "only novel↔New (both = unseen failure modes) is defensible. No tasks are shared.\n")
    L.append("| Family (ours) | rex pass@1 (A1) | rex_no_oracle pass@1 (A1) | ↔ SREGym partition | SREGym E2E (Claude Code, no noise) |")
    L.append("|---|---|---|---|---|")
    rows = [("simple", "ported"), ("cascade", "similar"), ("novel", "new")]
    for fam, part in rows:
        rex = fmt_pct(_get(a1.get("rex", {}).get(fam, {}), "p1"))
        rno = fmt_pct(_get(a1.get("rex_no_oracle", {}).get(fam, {}), "p1"))
        e2e = fmt_pct(pb[part]["e2e"])
        L.append(f"| `{fam}` | {rex} | {rno} | `{part}` | {e2e} |")
    L.append("")
    L.append("> Both benchmarks agree directionally on ONE thing: **novel/unseen failures are "
             "hardest.** SREGym E2E collapses on `new` (Claude Code 60.8%→28.2% ported→new); our "
             "single-attempt `rex_no_oracle` is also weakest off the simple family.\n")
    return "\n".join(L)


def selftest():
    s = load_sregym(HERE / "sregym_reported.json")
    assert fmt_pct(0.6068) == "60.7%", fmt_pct(0.6068)
    assert fmt_pct(None) == "—"
    assert fmt_pct(1.0) == "100.0%"
    assert s["n_problems"] == 90
    assert len(s["leaderboard"]) == 8
    a1 = HERE.parent.parent / "A1" / "artifacts" / "full_pass_at_k_glm-5p2.json"
    a2 = HERE.parent.parent / "A2" / "artifacts" / "ablation_pass_at_k_deepseek-v4-pro.json"
    our = load_our(a1, a2)
    rex_p1 = our["by_run"]["A1"]["rex"]["overall"]["p1"]
    assert abs(rex_p1 - 0.897) < 0.01, rex_p1
    assert len(our["by_run"]["A1"]) == 5, list(our["by_run"]["A1"])
    # per-family must be populated (regression guard for by_family nesting)
    assert our["by_run"]["A1"]["rex"]["novel"]["p1"] is not None
    assert abs(our["by_run"]["A1"]["rex"]["novel"]["p1"] - 1.0) < 0.01
    tbl = render_table(our, s)
    for tok in ("SREGym", "REx".lower() if False else "rex", "pass@1", "no SREGym counterpart"):
        assert tok in tbl, tok
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a1", default=str(HERE.parent.parent / "A1" / "artifacts" / "full_pass_at_k_glm-5p2.json"))
    ap.add_argument("--a2", default=str(HERE.parent.parent / "A2" / "artifacts" / "ablation_pass_at_k_deepseek-v4-pro.json"))
    ap.add_argument("--sregym", default=str(HERE / "sregym_reported.json"))
    ap.add_argument("--out-table", default=str(HERE / "comparison_table.md"))
    ap.add_argument("--out-our", default=str(HERE / "our_pass_at_1.json"))
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        selftest()
        return
    our = load_our(args.a1, args.a2)
    sregym = load_sregym(args.sregym)
    Path(args.out_our).write_text(json.dumps(our, indent=2))
    table = render_table(our, sregym)
    Path(args.out_table).write_text(table + "\n")
    print(table)
    print(f"\n[wrote {args.out_table} and {args.out_our}]", file=sys.stderr)


if __name__ == "__main__":
    main()
