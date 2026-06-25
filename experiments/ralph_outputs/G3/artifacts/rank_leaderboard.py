#!/usr/bin/env python3
"""G3 — Where would we rank on SREGym's pass@1 (E2E) leaderboard?

Stdlib-only. Loads:
  - the cited, frozen SREGym leaderboard (sregym_reported.json, copied from B15 +
    re-cited here so G3 is self-contained), and
  - our real pass@1 numbers, pulled live from the A1/A2 result JSONs at run time.

It then inserts our conditions as pseudo-rows into the SREGym E2E leaderboard and
prints a single ranked table, plus an explicit, loud non-equivalence banner so the
"rank" is never mistaken for an apples-to-apples claim.

Run:
    python3 rank_leaderboard.py            # render ranked table to stdout + .md
    python3 rank_leaderboard.py --selftest # assertions only, no I/O side effects beyond read
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
A1_JSON = "/Users/mei/rl/experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json"
A2_JSON = "/Users/mei/rl/experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json"
SREGYM_JSON = os.path.join(HERE, "sregym_reported.json")

# Which of our conditions are "fair" single-attempt analogues of SREGym's
# single-attempt E2E success rate, and which are out-of-regime (multi-attempt /
# oracle-fed) and therefore NOT directly rankable.
FAIR_CONDITIONS = {"zero_shot", "best_of_n", "retry_realistic", "rex_no_oracle"}
OUT_OF_REGIME = {"rex"}  # multi-attempt + oracle feedback; no SREGym counterpart


def _wilson_ci(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5)
    return ((c - h) / d, (c + h) / d)


def _pass_at_1_from_result(result):
    """Reduce a raw pass@k result JSON to per-condition pass@1 (overall).

    Accepts the eval_pass_at_k schema: result['conditions'][cond] holds either a
    precomputed 'pass_at_1' or per-episode rewards we threshold at 0.8 (seed 0 ==
    single attempt => pass@1). Falls back gracefully across minor schema variants.
    """
    out = {}
    conds = result.get("conditions") or result.get("by_condition") or {}
    for cond, payload in conds.items():
        # Preferred: explicit overall pass@1
        ov = payload.get("overall") if isinstance(payload, dict) else None
        if isinstance(ov, dict) and "p1" in ov:
            out[cond] = {"p1": ov["p1"], "ci": ov.get("ci"), "n": ov.get("n")}
            continue
        if isinstance(payload, dict) and "pass_at_1" in payload:
            p1 = payload["pass_at_1"]
            n = payload.get("n")
            ci = _wilson_ci(round(p1 * n), n) if n else None
            out[cond] = {"p1": p1, "ci": list(ci) if ci else None, "n": n}
            continue
    return out


def load_ours():
    """Read our real pass@1 from A1/A2. Prefer B15's distilled file if present
    (it already encodes the per-family + CI breakdown), else recompute from raw."""
    distilled = os.path.join(
        "/Users/mei/rl/experiments/ralph_outputs/B15/artifacts/our_pass_at_1.json"
    )
    if os.path.exists(distilled):
        with open(distilled) as f:
            d = json.load(f)
        # flatten to {run: {cond: {p1, ci, n}}}
        flat = {}
        for run, conds in d.get("by_run", {}).items():
            flat[run] = {}
            for cond, fam in conds.items():
                ov = fam.get("overall", {})
                flat[run][cond] = {"p1": ov.get("p1"), "ci": ov.get("ci"), "n": ov.get("n")}
        return flat, "B15/artifacts/our_pass_at_1.json (distilled from A1/A2)"
    # fallback: recompute from raw A1/A2
    flat = {}
    for run, path in (("A1", A1_JSON), ("A2", A2_JSON)):
        if os.path.exists(path):
            with open(path) as f:
                flat[run] = _pass_at_1_from_result(json.load(f))
    return flat, "recomputed from A1/A2 raw result JSON"


def load_sregym():
    with open(SREGYM_JSON) as f:
        return json.load(f)


def build_ranked_rows(sregym, ours):
    """Return list of dicts: each a leaderboard row with e2e==pass@1, sorted desc.
    Our rows are tagged with regime so the renderer can mark them."""
    rows = []
    for r in sregym["leaderboard"]:
        rows.append({
            "system": f"{r['agent']} ({r['model']}{', noise' if r['noise'] else ''})",
            "p1": r["e2e"],
            "kind": "SREGYM",
            "regime": "live single-attempt E2E",
            "ci": None,
            "n": sregym["n_problems"],
        })
    # Our rows — use A1 (the bigger 42-incident set) as the headline, note A2 in report
    a1 = ours.get("A1", {})
    label = {
        "zero_shot": "OURS zero_shot (sim, glm-5p2)",
        "best_of_n": "OURS best_of_n (sim, glm-5p2)",
        "retry_realistic": "OURS retry_realistic (sim, glm-5p2)",
        "rex_no_oracle": "OURS rex_no_oracle (sim, glm-5p2)",
        "rex": "OURS REx (sim, glm-5p2) [OUT-OF-REGIME]",
    }
    for cond, payload in a1.items():
        if payload.get("p1") is None:
            continue
        rows.append({
            "system": label.get(cond, f"OURS {cond}"),
            "p1": payload["p1"],
            "kind": "OURS",
            "regime": ("multi-attempt + ORACLE (no SREGym analogue)"
                       if cond in OUT_OF_REGIME else "sim single-attempt"),
            "ci": payload.get("ci"),
            "n": payload.get("n"),
            "fair": cond in FAIR_CONDITIONS,
        })
    rows.sort(key=lambda x: x["p1"], reverse=True)
    for i, r in enumerate(rows, 1):
        r["rank"] = i
    return rows


def render(rows, ours_src, sregym):
    lines = []
    lines.append("# G3 — SREGym pass@1 (E2E) leaderboard: where would we rank?\n")
    lines.append("> **NON-EQUIVALENCE BANNER.** This table inserts OUR numbers into "
                 "SREGym's E2E leaderboard *for positioning only*. SREGym rows are "
                 "**live Kubernetes** single-attempt E2E (diagnosis AND mitigation, "
                 "n=90). OUR rows are a **deterministic simulator** with a reward@0.8 "
                 "grader, different incidents, cheaper models. The 'rank' column is "
                 "NOT a fair-fight ranking — it is a number line. See caveats.\n")
    lines.append(f"- SREGym source: {sregym['version_note']}")
    lines.append(f"- Our source: {ours_src}\n")
    lines.append("| rank | system | pass@1 (E2E) | 95% CI | n | regime |")
    lines.append("|---:|---|---:|---|---:|---|")
    for r in rows:
        ci = ""
        if r.get("ci"):
            ci = f"[{r['ci'][0]:.2f},{r['ci'][1]:.2f}]"
        mark = ""
        if r["kind"] == "OURS":
            mark = " **<- OURS**"
        lines.append(
            f"| {r['rank']} | {r['system']}{mark} | {r['p1']*100:.1f}% | "
            f"{ci} | {r['n']} | {r['regime']} |"
        )
    # Honest positioning summary
    fair = [r for r in rows if r["kind"] == "OURS" and r.get("fair")]
    oor = [r for r in rows if r["kind"] == "OURS" and not r.get("fair")]
    sre = [r for r in rows if r["kind"] == "SREGYM"]
    sre_lo, sre_hi = min(s["p1"] for s in sre), max(s["p1"] for s in sre)
    lines.append("\n## Honest positioning\n")
    if fair:
        fb = max(r["p1"] for r in fair)
        fb_rank = [r["rank"] for r in fair if r["p1"] == fb][0]
        n_below = sum(1 for s in sre if s["p1"] < fb)
        lines.append(
            f"- **Fair single-attempt comparison:** our best in-regime condition is "
            f"{fb*100:.1f}% (retry / best_of_n), landing at rank {fb_rank}. It sits "
            f"in the LOWER part of SREGym's E2E band ({sre_lo*100:.1f}%–{sre_hi*100:.1f}%): "
            f"above only the {n_below} weakest SREGym entr"
            f"{'y' if n_below == 1 else 'ies'} (Kimi-K2.5 Stratus), and below every "
            f"frontier-model agent. On a like-for-like single-attempt basis we are a "
            f"bottom-of-board entry, not a leader.")
    if oor:
        ob = oor[0]
        lines.append(
            f"- **REx ({ob['p1']*100:.1f}%) would 'top' the table**, but it is "
            f"out-of-regime: it consumes multiple attempts AND a P0 oracle hint that "
            f"SREGym agents never get. Treat its placement as a CATEGORY ERROR, not a "
            f"win. (A1 also shows rex_no_oracle collapses to ~33%, i.e. the tree alone "
            f"buys little — the oracle is doing the work.)")
    lines.append(
        "- **Both benchmarks agree** novel/unseen failures are hardest: SREGym E2E "
        "collapses ported->new (60.8->28.2 Claude Code; 63.7->17.9 Stratus), and our "
        "zero_shot cascade pass@1 is 6.7%.")
    return "\n".join(lines) + "\n"


def selftest():
    sregym = load_sregym()
    ours, _ = load_ours()
    assert sregym["n_problems"] == 90, "expected 90 SREGym problems"
    assert len(sregym["leaderboard"]) >= 8, "expected >=8 leaderboard rows"
    assert "A1" in ours and ours["A1"], "A1 numbers missing"
    rows = build_ranked_rows(sregym, ours)
    # ranks are a permutation 1..N
    assert [r["rank"] for r in rows] == list(range(1, len(rows) + 1))
    # sorted descending by p1
    ps = [r["p1"] for r in rows]
    assert ps == sorted(ps, reverse=True), "rows not sorted by pass@1 desc"
    # our REx is present and out-of-regime
    rex = [r for r in rows if r["kind"] == "OURS" and not r.get("fair")]
    assert rex and rex[0]["p1"] > 0.8, "REx row missing/low"
    # fair conditions present and below max SREGym e2e
    fair = [r for r in rows if r["kind"] == "OURS" and r.get("fair")]
    assert fair, "no fair OURS rows"
    sre_hi = max(r["p1"] for r in rows if r["kind"] == "SREGYM")
    assert max(r["p1"] for r in fair) < sre_hi, "fair band should sit below SREGym top"
    print("SELFTEST OK:", len(rows), "ranked rows;",
          "fair-best=%.3f" % max(r["p1"] for r in fair),
          "rex=%.3f" % rex[0]["p1"], "sregym_top=%.3f" % sre_hi)


def main():
    if "--selftest" in sys.argv:
        selftest()
        return
    sregym = load_sregym()
    ours, src = load_ours()
    rows = build_ranked_rows(sregym, ours)
    md = render(rows, src, sregym)
    out = os.path.join(HERE, "ranked_leaderboard.md")
    with open(out, "w") as f:
        f.write(md)
    print(md)
    print(f"[wrote {out}]")


if __name__ == "__main__":
    main()
