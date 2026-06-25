#!/usr/bin/env python3
"""Render a compact human summary + test assertions from a full_pass_at_k_*.json.
Reads whichever of the final JSON or the .partial checkpoint exists (so a truncated
but real run is still reportable). Usage: python3 summarize_result.py [path]"""
import json, os, statistics as st, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "..", "..")))
from experiments.compute_pass_at_k import pass_at_k, wilson_ci, binary_pass  # noqa
from rex.eval_pass_at_k import THRESHOLD, pick_incidents  # noqa

path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "full_pass_at_k_glm-5p2.json")
partial = path + ".partial"
src = path if os.path.exists(path) else partial
d = json.load(open(src))

inc = pick_incidents(None)
fam_of = {n: f for f, ns in inc.items() for n in ns}
flat = [n for ns in inc.values() for n in ns]


def summ(rewards):
    n = len(rewards); c = sum(binary_pass(r, THRESHOLD) for r in rewards)
    p1 = c / n if n else 0.0; lo, hi = wilson_ci(p1, n)
    return dict(n=n, passes=c, p1=round(p1, 4), ci=[round(lo, 4), round(hi, 4)],
                p2=round(pass_at_k(n, c, 2), 4), p5=round(pass_at_k(n, c, 5), 4),
                mean=round(st.mean(rewards), 4) if rewards else 0,
                std=round(st.pstdev(rewards), 4) if len(rewards) > 1 else 0)


# rebuild by_condition from raw if reading the partial; else use stored
raw = d.get("raw")
if raw is None:
    by = {c: d["by_condition"][c] for c in d["by_condition"]}
    conds = list(by)
    get = lambda c, n: d["by_condition"][c]["per_incident_rewards"].get(n, [])
else:
    conds = list(raw)
    get = lambda c, n: raw[c].get(n, [])

print(f"source: {os.path.basename(src)}   threshold={THRESHOLD}")
print(f"incidents covered: {len(flat)} (simple={len(inc['simple'])}, cascade={len(inc['cascade'])}, novel={len(inc['novel'])})")
print(f"floor_check: {d.get('floor_check')}\n")
hdr = f"{'condition':<16}{'fam':<9}{'pass@1':>8}{'95% CI':>16}{'pass@2':>8}{'pass@5':>8}{'mean':>7}{'std':>7}{'n':>5}"
print(hdr); print("-" * len(hdr))
report = {}
for c in conds:
    allr = [r for n in flat for r in get(c, n)]
    if not allr:
        continue
    o = summ(allr)
    report.setdefault(c, {})["overall"] = o
    ci = f"[{o['ci'][0]:.2f},{o['ci'][1]:.2f}]"
    print(f"{c:<16}{'ALL':<9}{o['p1']:>8.3f}{ci:>16}{o['p2']:>8.3f}{o['p5']:>8.3f}{o['mean']:>7.2f}{o['std']:>7.2f}{o['n']:>5}")
    for f in ("simple", "cascade", "novel"):
        fr = [r for n in inc[f] for r in get(c, n)]
        if fr:
            s = summ(fr); report[c][f] = s
            ci = f"[{s['ci'][0]:.2f},{s['ci'][1]:.2f}]"
            print(f"{'':<16}{f:<9}{s['p1']:>8.3f}{ci:>16}{s['p2']:>8.3f}{s['p5']:>8.3f}{s['mean']:>7.2f}{s['std']:>7.2f}{s['n']:>5}")
json.dump(report, open(os.path.join(HERE, "summary_table.json"), "w"), indent=2)
print("\n-> summary_table.json")
