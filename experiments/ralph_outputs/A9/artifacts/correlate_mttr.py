#!/usr/bin/env python3
"""Correlation-analysis stub: real-world MTTR vs an agent/sim difficulty signal.

This is a STUB / scaffold (Task A9). It loads the MTTR labels produced by this
task and joins them against a per-incident difficulty/score signal, then reports
Spearman + Pearson correlation. The difficulty signal is pluggable:

    --scores PATH    JSON or CSV mapping incident_id -> numeric difficulty/score.
                     If omitted, falls back to a structural proxy derived from the
                     scenario YAML (node count + cascade/buried-gun flags) so the
                     script is runnable end-to-end with only repo assets.

Hypothesis under test (for the writeup): incidents that took humans longer to
resolve (higher real MTTR) are also harder for the agent (lower pass@k / higher
step count). Only incidents with a KNOWN MTTR are included; unknowns are dropped
and reported.

No third-party deps (no numpy/scipy required) so it runs in the base env.
"""
import argparse
import csv
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DEFAULT_LABELS = os.path.join(HERE, "mttr_labels.json")
GEN_DIR = os.path.join(REPO, "scenarios", "cidg", "generated")


def load_labels(path):
    with open(path) as f:
        return json.load(f)["incidents"]


def _rank(xs):
    order = sorted(range(len(xs)), key=lambda i: xs[i])
    ranks = [0.0] * len(xs)
    i = 0
    while i < len(xs):
        j = i
        while j + 1 < len(xs) and xs[order[j + 1]] == xs[order[i]]:
            j += 1
        avg = (i + j) / 2.0 + 1.0  # 1-based, ties averaged
        for k in range(i, j + 1):
            ranks[order[k]] = avg
        i = j + 1
    return ranks


def pearson(xs, ys):
    n = len(xs)
    if n < 2:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    dx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    dy = math.sqrt(sum((y - my) ** 2 for y in ys))
    if dx == 0 or dy == 0:
        return None
    return num / (dx * dy)


def spearman(xs, ys):
    return pearson(_rank(xs), _rank(ys))


def load_scores(path):
    if path.endswith(".json"):
        with open(path) as f:
            d = json.load(f)
        return {k: float(v) for k, v in d.items()}
    out = {}
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out[row["incident_id"]] = float(row["score"])
    return out


def structural_proxy(incident_id, yaml_file):
    """Fallback difficulty proxy from the scenario YAML, no PyYAML needed."""
    path = os.path.join(GEN_DIR, yaml_file)
    if not os.path.exists(path):
        return None
    nodes = 0
    cascade = buried = 0
    with open(path) as f:
        for line in f:
            s = line.strip()
            if s.startswith("- name:"):
                nodes += 1
            if s == "cascades: true":
                cascade = 1
            if s == "buried_gun_exists: true":
                buried = 1
    return nodes + 3 * cascade + 2 * buried


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default=DEFAULT_LABELS)
    ap.add_argument("--scores", default=None,
                    help="incident_id->difficulty (json/csv). Default: structural proxy.")
    args = ap.parse_args()

    incidents = load_labels(args.labels)
    scores = load_scores(args.scores) if args.scores else None

    paired, dropped = [], []
    for rec in incidents:
        iid = rec["incident_id"]
        mttr = rec["mttr_minutes"]
        if mttr is None:
            dropped.append((iid, "unknown_mttr"))
            continue
        if scores is not None:
            if iid not in scores:
                dropped.append((iid, "no_score"))
                continue
            sig = scores[iid]
        else:
            sig = structural_proxy(iid, rec["yaml_file"])
            if sig is None:
                dropped.append((iid, "no_yaml"))
                continue
        paired.append((iid, float(mttr), float(sig)))

    print(f"paired={len(paired)}  dropped={len(dropped)}")
    for iid, reason in dropped:
        print(f"  dropped {iid}: {reason}")

    if len(paired) < 2:
        print("\nNot enough paired points for correlation (need >=2 known-MTTR incidents).")
        return

    xs = [p[1] for p in paired]
    ys = [p[2] for p in paired]
    sig_name = "external_score" if scores else "structural_proxy"
    print(f"\nsignal = {sig_name}")
    print(f"pearson(mttr, {sig_name})  = {pearson(xs, ys)}")
    print(f"spearman(mttr, {sig_name}) = {spearman(xs, ys)}")
    print("\nper-incident:")
    for iid, m, s in sorted(paired, key=lambda p: -p[1]):
        print(f"  {iid:32s} mttr={m:7.0f}min  {sig_name}={s:g}")


if __name__ == "__main__":
    main()
