#!/usr/bin/env python3
"""Generate a synthetic Fireball-format fixture corpus for validating the sweep
harness WITHOUT touching the real data and WITHOUT fabricating scaling numbers.

The fixture mimics the real `trajectories.jsonl` shape (trajectory_id, incident,
difficulty, trajectory[]) across several families and difficulties so the
stratified subsetter has something realistic to apportion over. It contains NO
reward/score field — scores only ever come from a real fit callback.
"""
import argparse
import json
import random
from pathlib import Path

FAMILIES = ["bad_deploy_errors", "cache_stampede", "cert_expiry", "crashloop",
            "db_pool_exhaustion", "disk_pressure", "dns_failure", "oom_kill"]
DIFFS = [3, 4, 5]


def make(n: int, seed: int = 0) -> list[dict]:
    rng = random.Random(seed)
    out = []
    for i in range(n):
        fam = rng.choice(FAMILIES)
        diff = rng.choices(DIFFS, weights=[0.3, 0.6, 0.1])[0]
        nsteps = rng.choice([8, 10, 12, 14])
        traj = []
        for s in range(nsteps):
            role = "assistant" if s % 2 == 0 else "tool"
            traj.append({"step": s, "role": role,
                         "thought": f"step {s} on {fam}" if role == "assistant" else None,
                         "action": {"tool": "get_logs"} if role == "assistant" else None})
        out.append({
            "trajectory_id": f"{fam}_{i:05d}",
            "provider": "k8s", "incident": fam,
            "scenario_id": f"{rng.randint(1,99):03d}-{fam}",
            "difficulty": diff, "source": "synthetic-fixture",
            "trajectory": traj,
        })
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=str(Path(__file__).with_name("fixture_corpus.jsonl")))
    a = ap.parse_args()
    recs = make(a.n, a.seed)
    with open(a.out, "w") as f:
        for r in recs:
            f.write(json.dumps(r) + "\n")
    print(f"wrote {len(recs)} records -> {a.out}")


if __name__ == "__main__":
    main()
