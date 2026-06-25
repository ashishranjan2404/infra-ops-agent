#!/usr/bin/env python3
"""B1 — summarize a grid result JSON into a compact table + summary_table.json.

Usage:
    python3 experiments/ralph_outputs/B1/artifacts/summarize_grid.py \
        experiments/ralph_outputs/B1/artifacts/grid_sub2_glm-5p2.json
"""
import json
import os
import sys


def main(path):
    d = json.load(open(path))
    grid = d.get("grid", {})
    print(f"model={d.get('label', d.get('model'))}  seeds={d.get('seeds')}  "
          f"threshold={d.get('threshold')}  episodes={grid.get('episodes')}  "
          f"full_grid={grid.get('full_grid')}  errors={d.get('n_errors')}")
    fc = d.get("floor_check", {})
    print(f"floor: empty={fc.get('empty_plan_max_reward')} trap={fc.get('trap_max_reward')} "
          f"-> {'OK' if fc.get('floor_ok') else 'LEAK'}")
    print(f"\n{'condition':<18}{'pass@1':>8}{'95% CI':>16}{'pass@2':>8}{'pass@5':>8}{'mean':>7}{'std':>7}{'n':>5}")
    print("-" * 84)
    table = {}
    for cond, dd in d["by_condition"].items():
        o = dd["overall"]
        ci = f"[{o['ci95'][0]:.2f},{o['ci95'][1]:.2f}]"
        print(f"{cond:<18}{o['pass@1']:>8.3f}{ci:>16}{o['pass@2']:>8.3f}"
              f"{o['pass@5']:>8.3f}{o['mean_reward']:>7.2f}{o['reward_std']:>7.2f}{o['n']:>5}")
        table[cond] = {"pass@1": o["pass@1"], "ci95": o["ci95"], "pass@2": o["pass@2"],
                       "pass@5": o["pass@5"], "mean": o["mean_reward"],
                       "std": o["reward_std"], "n": o["n"]}
    # thesis line
    if "rex" in table and "zero_shot" in table:
        rx, zs = table["rex"], table["zero_shot"]
        disjoint = rx["ci95"][0] > zs["ci95"][1]
        print(f"\nthesis: rex pass@1={rx['pass@1']:.3f} {rx['ci95']} vs "
              f"zero_shot pass@1={zs['pass@1']:.3f} {zs['ci95']}  "
              f"-> CIs {'DISJOINT' if disjoint else 'overlap'}")
    out = {"model": d.get("model"), "seeds": d.get("seeds"),
           "episodes": grid.get("episodes"), "full_grid": grid.get("full_grid"),
           "floor_ok": fc.get("floor_ok"), "by_condition": table}
    outp = os.path.join(os.path.dirname(os.path.abspath(path)), "summary_table.json")
    json.dump(out, open(outp, "w"), indent=2)
    print(f"\n-> {outp}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else
         os.path.join(os.path.dirname(__file__), "grid_sub2_glm-5p2.json"))
