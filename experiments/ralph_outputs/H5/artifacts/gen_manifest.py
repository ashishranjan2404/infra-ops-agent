#!/usr/bin/env python3
"""H5 promotion-engine: build a results manifest from REAL A1/A2 pass@k outputs.

Reads two existing, real artifacts produced by other Ralph workers:
  - A1: experiments/ralph_outputs/A1/artifacts/summary_table.json   (model glm-5p2)
  - A2: experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json

and normalizes them into one promotion-gate manifest consumed by dashboard.html.

A "candidate" is one (model, condition). The promotion gate decides PROMOTE /
HOLD / REJECT from the candidate's pass@1, its 95% CI lower bound, and the gap to
the zero_shot baseline for the same model.

The manifest format is the stable contract between this generator and the HTML:

{
  "schema": "sre-degrees.promotion-manifest/v1",
  "generated_at": "<iso8601>",
  "gate": {"promote_p1": 0.80, "promote_ci_lo": 0.70, "min_lift_over_baseline": 0.20},
  "families": ["simple","cascade","novel"],
  "candidates": [
    {
      "id": "glm-5p2/rex",
      "model": "glm-5p2",
      "condition": "rex",
      "source": "A1",
      "n": 126, "passes": 113,
      "pass_at_1": 0.8968, "ci_lo": 0.8315, "ci_hi": 0.9387,
      "pass_at_2": 0.9901, "pass_at_5": 1.0,
      "lift_over_baseline": 0.6666,
      "by_family": {"simple": {...}, "cascade": {...}, "novel": {...}},
      "decision": "PROMOTE", "reasons": [...]
    }, ...
  ]
}
"""
import json
import os
import datetime

REPO = "/Users/mei/rl"
A1 = os.path.join(REPO, "experiments/ralph_outputs/A1/artifacts/summary_table.json")
A2 = os.path.join(REPO, "experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json")
OUT = os.path.join(os.path.dirname(__file__), "sample_manifest.json")

# Promotion gate thresholds (a candidate must clear ALL to PROMOTE).
GATE = {
    "promote_p1": 0.80,           # observed pass@1 must be >= this
    "promote_ci_lo": 0.70,        # 95% CI lower bound must be >= this (robustness)
    "min_lift_over_baseline": 0.20,  # must beat its own zero_shot baseline by this much
}
FAMILIES = ["simple", "cascade", "novel"]


def _round(x, n=4):
    return round(float(x), n) if x is not None else None


def decide(p1, ci_lo, lift):
    """Return (decision, reasons) given the gate."""
    reasons = []
    pass_p1 = p1 >= GATE["promote_p1"]
    pass_ci = ci_lo >= GATE["promote_ci_lo"]
    pass_lift = lift >= GATE["min_lift_over_baseline"]
    reasons.append(("pass@1 %.2f >= %.2f" % (p1, GATE["promote_p1"])) if pass_p1
                    else ("pass@1 %.2f < %.2f" % (p1, GATE["promote_p1"])))
    reasons.append(("CI_lo %.2f >= %.2f" % (ci_lo, GATE["promote_ci_lo"])) if pass_ci
                    else ("CI_lo %.2f < %.2f" % (ci_lo, GATE["promote_ci_lo"])))
    reasons.append(("lift %.2f >= %.2f" % (lift, GATE["min_lift_over_baseline"])) if pass_lift
                    else ("lift %.2f < %.2f" % (lift, GATE["min_lift_over_baseline"])))
    if pass_p1 and pass_ci and pass_lift:
        return "PROMOTE", reasons
    # REJECT if it does not even clear the baseline-lift bar; otherwise HOLD.
    if not pass_lift:
        return "REJECT", reasons
    return "HOLD", reasons


def load_a1():
    """A1 summary_table.json: {condition: {overall:{...}, simple:{...}, ...}}."""
    d = json.load(open(A1))
    base = d["zero_shot"]["overall"]["p1"]
    out = []
    for cond, blk in d.items():
        ov = blk["overall"]
        p1 = ov["p1"]
        rec = {
            "id": "glm-5p2/" + cond,
            "model": "glm-5p2",
            "condition": cond,
            "source": "A1",
            "n": ov["n"], "passes": ov["passes"],
            "pass_at_1": _round(p1),
            "ci_lo": _round(ov["ci"][0]), "ci_hi": _round(ov["ci"][1]),
            "pass_at_2": _round(ov.get("p2")), "pass_at_5": _round(ov.get("p5")),
            "lift_over_baseline": _round(p1 - base),
            "by_family": {},
        }
        for fam in FAMILIES:
            if fam in blk:
                fb = blk[fam]
                rec["by_family"][fam] = {
                    "n": fb["n"], "pass_at_1": _round(fb["p1"]),
                    "ci_lo": _round(fb["ci"][0]), "ci_hi": _round(fb["ci"][1]),
                }
        dec, why = decide(p1, ov["ci"][0], rec["lift_over_baseline"])
        rec["decision"] = dec
        rec["reasons"] = why
        out.append(rec)
    return out


def load_a2():
    """A2 ablation json: {by_condition: {cond: {overall:{...}, by_family:{...}}}}."""
    d = json.load(open(A2))
    bc = d["by_condition"]
    base = bc["zero_shot"]["overall"]["pass@1"]
    out = []
    for cond, blk in bc.items():
        ov = blk["overall"]
        p1 = ov["pass@1"]
        rec = {
            "id": "deepseek-v4-pro/" + cond,
            "model": "deepseek-v4-pro",
            "condition": cond,
            "source": "A2",
            "n": ov["n"], "passes": ov["passes"],
            "pass_at_1": _round(p1),
            "ci_lo": _round(ov["ci95"][0]), "ci_hi": _round(ov["ci95"][1]),
            "pass_at_2": _round(ov.get("pass@2")), "pass_at_5": _round(ov.get("pass@5")),
            "lift_over_baseline": _round(p1 - base),
            "by_family": {},
        }
        for fam in FAMILIES:
            fb = blk.get("by_family", {}).get(fam)
            if fb:
                rec["by_family"][fam] = {
                    "n": fb["n"], "pass_at_1": _round(fb["pass@1"]),
                    "ci_lo": _round(fb["ci95"][0]), "ci_hi": _round(fb["ci95"][1]),
                }
        dec, why = decide(p1, ov["ci95"][0], rec["lift_over_baseline"])
        rec["decision"] = dec
        rec["reasons"] = why
        out.append(rec)
    return out


def main():
    candidates = load_a1() + load_a2()
    manifest = {
        "schema": "sre-degrees.promotion-manifest/v1",
        "generated_at": datetime.datetime.now(datetime.timezone.utc)
            .isoformat(timespec="seconds"),
        "gate": GATE,
        "families": FAMILIES,
        "sources": {
            "A1": "ralph_outputs/A1/artifacts/summary_table.json (glm-5p2, 630 episodes)",
            "A2": "ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json (750 episodes)",
        },
        "candidates": candidates,
    }
    with open(OUT, "w") as f:
        json.dump(manifest, f, indent=2)
    n_prom = sum(1 for c in candidates if c["decision"] == "PROMOTE")
    print("wrote %s" % OUT)
    print("candidates=%d  PROMOTE=%d  HOLD=%d  REJECT=%d" % (
        len(candidates), n_prom,
        sum(1 for c in candidates if c["decision"] == "HOLD"),
        sum(1 for c in candidates if c["decision"] == "REJECT")))
    for c in candidates:
        print("  %-28s p1=%.3f ci_lo=%.3f lift=%+.3f -> %s"
              % (c["id"], c["pass_at_1"], c["ci_lo"], c["lift_over_baseline"], c["decision"]))


if __name__ == "__main__":
    main()
