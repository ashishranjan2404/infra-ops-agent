"""
Run Hartigan's dip test on REAL per-episode reward distributions from this repo.

Data sources (all real, committed rollout/result data):
  - A1: experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json
        (glm-5p2, 5 conditions x 126 episodes; per_incident_rewards)
  - A2: experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json
        (deepseek-v4-pro, 5 conditions x 150 episodes; per_incident_rewards)
  - rex/runs/diagnostic_probe_*.jsonl (per-iteration `score`)

We test each per-episode reward vector for unimodality vs (bi/multi)modality.
The "bimodal distribution" hypothesis for these incident-resolution rewards is
that rewards pile up near 0 (failed) and near 1 (clean win) with a thin middle —
classic pass/fail bimodality. The dip test quantifies that.

Output: experiments/ralph_outputs/I3/artifacts/dip_results.json
"""
from __future__ import annotations
import json, os, glob, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dip_test import dip_test  # noqa: E402

REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
A1 = os.path.join(REPO, "experiments/ralph_outputs/A1/artifacts/full_pass_at_k_glm-5p2.json")
A2 = os.path.join(REPO, "experiments/ralph_outputs/A2/artifacts/ablation_pass_at_k_deepseek-v4-pro.json")
SEED = 0


def collect_condition_rewards(path):
    d = json.load(open(path))
    out = {}
    for cond, v in d.get("by_condition", {}).items():
        pir = v.get("per_incident_rewards", {})
        rewards = [float(x) for arr in pir.values() for x in arr]
        if rewards:
            out[cond] = rewards
    return d.get("model", os.path.basename(path)), out


def collect_rex_runs(repo):
    scores = []
    for f in glob.glob(os.path.join(repo, "rex/runs/diagnostic_probe_*.jsonl")):
        for line in open(f):
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            if "score" in obj:
                scores.append(float(obj["score"]))
    return scores


def describe(rewards):
    a = np.asarray(rewards, dtype=float)
    # fraction near the two poles vs the middle
    lo = float(np.mean(a <= 0.1))
    hi = float(np.mean(a >= 0.9))
    mid = float(np.mean((a > 0.1) & (a < 0.9)))
    return {
        "n": int(a.size),
        "mean": round(float(a.mean()), 4),
        "std": round(float(a.std()), 4),
        "frac_low(<=0.1)": round(lo, 4),
        "frac_high(>=0.9)": round(hi, 4),
        "frac_mid": round(mid, 4),
    }


def run_one(name, rewards):
    D, p = dip_test(rewards)
    stats = describe(rewards)
    # Conclusion at alpha = 0.05
    if p < 0.05:
        concl = "REJECT unimodality (multimodal / bimodal)"
    elif p < 0.10:
        concl = "marginal (suggestive of multimodality)"
    else:
        concl = "fail to reject unimodality"
    return {
        "name": name,
        "dip_statistic": round(float(D), 5),
        "p_value": round(float(p), 5),
        "alpha": 0.05,
        "conclusion": concl,
        **stats,
    }


def main():
    results = []

    for path, tag in [(A1, "A1/glm-5p2"), (A2, "A2/deepseek-v4-pro")]:
        if not os.path.exists(path):
            continue
        model, conds = collect_condition_rewards(path)
        for cond, rewards in conds.items():
            results.append(run_one(f"{tag}::{cond}", rewards))
        # pooled across all conditions for this run
        pooled = [x for rs in conds.values() for x in rs]
        results.append(run_one(f"{tag}::ALL_CONDITIONS_pooled", pooled))

    rex_scores = collect_rex_runs(REPO)
    if rex_scores:
        results.append(run_one("rex/runs::diagnostic_probe_scores", rex_scores))

    out = {
        "test": "Hartigan & Hartigan (1985) dip test of unimodality",
        "engine": "diptest v0.11 (AS 217 C routine), analytic p-value table",
        "null": "Uniform(0,1) least-favourable unimodal null",
        "alpha": 0.05,
        "results": results,
    }
    out_path = os.path.join(HERE, "dip_results.json")
    json.dump(out, open(out_path, "w"), indent=2)

    # Pretty console table
    print(f"{'distribution':40s} {'n':>4s} {'dip':>7s} {'p':>8s}  conclusion")
    print("-" * 100)
    for r in results:
        print(f"{r['name']:40s} {r['n']:>4d} {r['dip_statistic']:>7.4f} "
              f"{r['p_value']:>8.4f}  {r['conclusion']}")
    print(f"\nWrote {out_path}")
    return out


if __name__ == "__main__":
    main()
