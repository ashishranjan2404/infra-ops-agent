#!/usr/bin/env python3
"""B4 — Render 3 stratified pass@k tables (simple / cascade / novel) from available results.

Pulls PRE-COMPUTED per-family numbers straight from each result JSON's
  by_condition[<cond>].by_family[<type>]
block (computed by rex.eval_pass_at_k with the canonical estimator in
experiments/compute_pass_at_k.py). It does NOT re-estimate pass@k — this guarantees the B4
tables are identical to the A1/A2 published numbers (see B4/05_ouroboros.md, problem 2.1/3.1).

For each type it emits one Markdown table across (source_file x model x condition), plus a
combined JSON. It cross-checks each result's own `incidents_by_family` against the B4 classifier
(incident_types.json) and reports mismatches. `.partial` result files are reported separately as
provisional and excluded from the headline tables (see grill, DOL).

Read-only on results. Writes only into B4/artifacts/.
"""
from __future__ import annotations

import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TYPES = ("simple", "cascade", "novel")
CLASSIFIER_JSON = os.path.join(HERE, "incident_types.json")

SEARCH = [
    os.path.join(REPO, "experiments", "results", "*pass_at_k*.json"),
    os.path.join(REPO, "experiments", "results", "*pass_at_k*.json.partial"),
    os.path.join(REPO, "experiments", "ralph_outputs", "*", "artifacts", "*pass_at_k*.json"),
]


def discover():
    headline, partial = [], []
    seen = set()
    for pat in SEARCH:
        for p in sorted(glob.glob(pat)):
            if p in seen:
                continue
            seen.add(p)
            (partial if p.endswith(".partial") else headline).append(p)
    return headline, partial


def fmt(x, nd=4):
    return "—" if x is None else f"{x:.{nd}f}"


def fmt_ci(blk):
    ci = blk.get("ci95")
    p1 = blk.get("pass@1")
    if p1 is None:
        return "—"
    if not ci:
        return fmt(p1, 4)
    return f"{p1:.3f} [{ci[0]:.3f},{ci[1]:.3f}]"


def collect_rows(results, ftype):
    """rows for one type across all headline results, keyed by (file,model,condition)."""
    rows = []
    for path, res in results:
        model = res.get("model", "?")
        src = os.path.relpath(path, REPO)
        for cond, cblk in (res.get("by_condition") or {}).items():
            fam = (cblk.get("by_family") or {}).get(ftype)
            if not fam:
                continue
            rows.append({
                "source": src, "model": model, "condition": cond,
                "n": fam.get("n"), "passes": fam.get("passes"),
                "pass@1": fam.get("pass@1"), "ci95": fam.get("ci95"),
                "pass@2": fam.get("pass@2"), "pass@5": fam.get("pass@5"),
                "mean_reward": fam.get("mean_reward"), "reward_std": fam.get("reward_std"),
            })
    return rows


def render_table(ftype, rows, unevaluated, partial_files):
    out = [f"# pass@k — incident type: {ftype}", ""]
    out.append("Numbers are pulled verbatim from each run's `by_condition[*].by_family"
               f"['{ftype}']` block (canonical estimator; no re-computation).")
    out.append("")
    if not rows:
        out.append(f"_No evaluated incidents of type `{ftype}` in any headline result file._")
    else:
        out.append("| source run | model | condition | n | passes | pass@1 (CI95) | "
                   "pass@2 | pass@5 | mean_r | std |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        for r in rows:
            out.append("| {src} | {m} | {c} | {n} | {p} | {p1} | {p2} | {p5} | {mr} | {sd} |".format(
                src=os.path.basename(r["source"]), m=r["model"], c=r["condition"],
                n=r["n"], p=r["passes"], p1=fmt_ci(r),
                p2=fmt(r["pass@2"], 4), p5=fmt(r["pass@5"], 4),
                mr=fmt(r["mean_reward"], 4), sd=fmt(r["reward_std"], 4)))
    out.append("")
    out.append(f"**Classified `{ftype}` incidents not evaluated in any headline run "
               f"({len(unevaluated)}):** " + (", ".join(sorted(unevaluated)) or "none"))
    if partial_files:
        out.append("")
        out.append("_Provisional (excluded above): " +
                   ", ".join(os.path.basename(p) for p in partial_files) + "._")
    out.append("")
    return "\n".join(out)


def consistency(results, classifier):
    """Compare each result's incidents_by_family vs B4 classifier labels."""
    cls = {}
    for inc in classifier["incidents"]:
        cls[inc["incident_id"].replace("-", "_").lower()] = inc["type"]
    mism = []
    for path, res in results:
        ibf = res.get("incidents_by_family") or {}
        for ftype, ids in ibf.items():
            for iid in ids:
                key = iid.replace("-", "_").lower()
                got = cls.get(key)
                if got is not None and got != ftype:
                    mism.append({"source": os.path.relpath(path, REPO), "incident": iid,
                                 "result_family": ftype, "b4_classifier": got})
    return mism


def main():
    classifier = json.load(open(CLASSIFIER_JSON))
    headline_paths, partial_paths = discover()
    results = [(p, json.load(open(p))) for p in headline_paths]

    # evaluated incident ids per type across headline runs
    evaluated = {t: set() for t in TYPES}
    for _, res in results:
        for t, ids in (res.get("incidents_by_family") or {}).items():
            if t in evaluated:
                evaluated[t].update(i.replace("-", "_").lower() for i in ids)

    classified_by_type = {t: set() for t in TYPES}
    for inc in classifier["incidents"]:
        classified_by_type[inc["type"]].add(inc["incident_id"].replace("-", "_").lower())

    tables_json = {}
    for ftype in TYPES:
        rows = collect_rows(results, ftype)
        uneval = classified_by_type[ftype] - evaluated[ftype]
        md = render_table(ftype, rows, uneval, partial_paths)
        with open(os.path.join(HERE, f"stratified_{ftype}.md"), "w") as fh:
            fh.write(md)
        tables_json[ftype] = {"rows": rows, "classified_unevaluated": sorted(uneval)}

    mism = consistency(results, classifier)
    combined = {
        "types": list(TYPES),
        "results_used": [os.path.relpath(p, REPO) for p in headline_paths],
        "partial_results": [os.path.relpath(p, REPO) for p in partial_paths],
        "classifier": "experiments/ralph_outputs/B4/artifacts/incident_types.json",
        "tables": tables_json,
        "consistency_mismatches": mism,
    }
    json.dump(combined, open(os.path.join(HERE, "stratified_pass_at_k.json"), "w"), indent=1)

    print(f"headline results: {[os.path.basename(p) for p in headline_paths]}")
    print(f"partial (provisional): {[os.path.basename(p) for p in partial_paths]}")
    for ftype in TYPES:
        n = len(tables_json[ftype]["rows"])
        u = len(tables_json[ftype]["classified_unevaluated"])
        print(f"  {ftype}: {n} table rows, {u} classified-but-unevaluated")
    print(f"classifier-vs-result mismatches: {len(mism)}")
    print("wrote stratified_{simple,cascade,novel}.md + stratified_pass_at_k.json")


if __name__ == "__main__":
    main()
