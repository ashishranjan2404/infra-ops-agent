#!/usr/bin/env python3
"""B3 — Wilson 95% confidence intervals for every pass@k point estimate.

This is a SELF-CONTAINED tool. It does not import or edit any shared core file
(rex/*, sim/*, experiments/*.py). It re-derives the Wilson score interval from
first principles (so it can be unit-tested against a known formula), then walks
the A1/A2 pass@k result JSONs, attaches a Wilson interval to every (condition,
family) pass@1 point estimate, and emits a flat table + a machine-readable JSON.

Why Wilson (not normal-approximation / Wald): the Wald interval p ± z·sqrt(p(1-p)/n)
collapses to width 0 at p=0 or p=1 and under-covers for small n — exactly the
regime of these pass@k tables (n as small as 30, many cells at p=0). The Wilson
score interval stays inside [0,1], has a non-degenerate width at the boundaries,
and has near-nominal coverage for small n (Brown, Cai & DasGupta 2001).

Wilson score interval for a binomial proportion (z = 1.96 for 95%):

            p_hat + z^2/(2n)        z             p_hat(1-p_hat)    z^2
   center = ----------------   ±  ------- · sqrt( --------------- + ----- )
              1 + z^2/n           1+z^2/n               n           4n^2

Usage:
    python3 wilson_ci.py                 # auto-discover A1/A2 JSONs, print table
    python3 wilson_ci.py f1.json f2.json # explicit inputs
    python3 wilson_ci.py --json out.json # also write machine-readable output
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from typing import Iterator

Z95 = 1.959963984540054  # exact two-sided 95% normal quantile


def wilson_ci(passes: int, n: int, z: float = Z95) -> tuple[float, float]:
    """Wilson score interval for `passes` successes out of `n` Bernoulli trials.

    Returns (lo, hi) clamped to [0, 1]. For n == 0 returns (0.0, 1.0) — with no
    data the only honest 95% statement is the whole unit interval.
    """
    if n < 0 or passes < 0 or passes > n:
        raise ValueError(f"need 0 <= passes <= n, got passes={passes}, n={n}")
    if n == 0:
        return (0.0, 1.0)
    p = passes / n
    z2 = z * z
    denom = 1.0 + z2 / n
    center = (p + z2 / (2.0 * n)) / denom
    half = (z / denom) * math.sqrt(p * (1.0 - p) / n + z2 / (4.0 * n * n))
    return (max(0.0, center - half), min(1.0, center + half))


def point_estimate(passes: int, n: int) -> float:
    return passes / n if n else 0.0


# ---------------------------------------------------------------------------
# Parsing the A1/A2 pass@k result schema.
# Each file: { "model", "label", "by_condition": { <cond>: {
#   "overall": {"n","passes","pass@1", "ci95":[lo,hi], ...},
#   "by_family": { <fam>: {"n","passes","pass@1","ci95", ...} } } } }
# ---------------------------------------------------------------------------
def iter_cells(doc: dict) -> Iterator[dict]:
    """Yield one row dict per (condition, scope) pass@1 point estimate."""
    label = doc.get("label") or doc.get("model") or "?"
    for cond, body in doc.get("by_condition", {}).items():
        overall = body.get("overall")
        if overall and "n" in overall:
            yield _cell(label, cond, "overall", overall)
        for fam, fbody in (body.get("by_family") or {}).items():
            if "n" in fbody:
                yield _cell(label, cond, fam, fbody)


def _cell(label: str, cond: str, scope: str, m: dict) -> dict:
    n = int(m["n"])
    passes = int(m["passes"])
    p = point_estimate(passes, n)
    lo, hi = wilson_ci(passes, n)
    stored = m.get("ci95")  # the CI the upstream tool recorded, for cross-check
    return {
        "condition": label + " / " + cond,
        "scope": scope,
        "n": n,
        "passes": passes,
        "pass@1": round(p, 4),
        "wilson_lo": round(lo, 4),
        "wilson_hi": round(hi, 4),
        "half_width": round((hi - lo) / 2.0, 4),
        "stored_ci95": [round(stored[0], 4), round(stored[1], 4)] if stored else None,
    }


def discover_inputs() -> list[str]:
    here = os.path.dirname(os.path.abspath(__file__))
    ral = os.path.dirname(os.path.dirname(here))  # experiments/ralph_outputs
    cands = [
        os.path.join(ral, "A1", "artifacts", "full_pass_at_k_glm-5p2.json"),
        os.path.join(ral, "A2", "artifacts", "ablation_pass_at_k_deepseek-v4-pro.json"),
    ]
    return [c for c in cands if os.path.exists(c)]


def build_rows(paths: list[str]) -> list[dict]:
    rows: list[dict] = []
    for p in paths:
        try:
            doc = json.loads(open(p).read())
        except Exception as e:  # noqa: BLE001
            print(f"WARN: skip {p}: {e}", file=sys.stderr)
            continue
        rows.extend(iter_cells(doc))
    return rows


def format_table(rows: list[dict]) -> str:
    out = []
    hdr = f"{'condition':<34}{'scope':<9}{'n':>5}{'pass@1':>9}{'  Wilson 95% CI':<20}{'±':>8}{'  match?':>9}"
    out.append(hdr)
    out.append("-" * len(hdr))
    for r in rows:
        ci = f"[{r['wilson_lo']:.3f}, {r['wilson_hi']:.3f}]"
        match = ""
        if r["stored_ci95"]:
            d = max(abs(r["wilson_lo"] - r["stored_ci95"][0]),
                    abs(r["wilson_hi"] - r["stored_ci95"][1]))
            match = "ok" if d <= 0.01 else f"DIFF {d:.3f}"
        out.append(f"{r['condition']:<34}{r['scope']:<9}{r['n']:>5}"
                   f"{r['pass@1']:>9.3f}  {ci:<18}{r['half_width']:>8.3f}{match:>9}")
    return "\n".join(out)


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="Wilson 95% CIs for pass@k tables")
    ap.add_argument("inputs", nargs="*", help="pass@k result JSON files")
    ap.add_argument("--json", dest="json_out", default=None, help="write rows as JSON")
    args = ap.parse_args(argv)

    paths = args.inputs or discover_inputs()
    if not paths:
        print("No pass@k JSON inputs found.", file=sys.stderr)
        return 2

    rows = build_rows(paths)
    print(f"# Wilson 95% CIs over {len(rows)} pass@1 cells from {len(paths)} file(s)")
    print(format_table(rows))

    if args.json_out:
        with open(args.json_out, "w") as f:
            json.dump({"z": Z95, "inputs": paths, "rows": rows}, f, indent=2)
        print(f"\nwrote {args.json_out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
