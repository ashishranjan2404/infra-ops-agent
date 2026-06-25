#!/usr/bin/env python3
"""
E6 ablation harness — full vs state-only vs action-only.

Pipeline:
  1. read a FIREBALL-format trajectory corpus (JSONL).
  2. emit the three ablated training corpora (via fireball_ablate transforms).
  3. report deterministic *structural* stats per variant (record counts, mean
     steps, channel composition). These are facts about the DATA, not model
     metrics — they prove the ablation is well-formed and non-degenerate.

What this harness does NOT do (BLOCKER):
  Train/eval a model on each variant. That needs (a) the real FIREBALL D&D SFT
  corpus, which is NOT in the repo (see experiments/results/P7_fireball_status.md
  and task E2), and (b) Wenji's GRPO training setup / a fireball-trained slug.
  When those land, point --in at the real corpus, then feed each emitted variant
  into the existing SFT/GRPO path and score with rex.eval_pass_at_k +
  rex.scoring (the deterministic judge) on the cascade benchmark. The data
  transform layer — the only genuinely new piece E6 owns — is complete and
  tested here.

Usage:
  python3 run_ablation_e6.py --in fixture_fireball.jsonl --outdir ./_variants
"""
from __future__ import annotations

import argparse
import json
import os
import statistics
from typing import Any, Dict, List

import fireball_ablate as fa


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    with open(path) as f:
        return [json.loads(l) for l in f if l.strip()]


def _channel_counts(rec: Dict[str, Any]) -> Dict[str, int]:
    traj = rec.get("trajectory", [])
    return {
        "assistant": sum(1 for s in traj if s.get("role") == "assistant"),
        "tool": sum(1 for s in traj if s.get("role") == "tool"),
    }


def variant_stats(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    steps = [len(r.get("trajectory", [])) for r in records]
    asst = sum(_channel_counts(r)["assistant"] for r in records)
    tool = sum(_channel_counts(r)["tool"] for r in records)
    has_state_rem = sum(
        1 for r in records
        if isinstance(r.get("remediation"), dict) and "state_after" in r["remediation"]
    )
    has_fix = sum(
        1 for r in records
        if isinstance(r.get("remediation"), dict) and "canonical_fix" in r["remediation"]
    )
    has_evidence = sum(1 for r in records if r.get("evidence"))
    return {
        "n_records": len(records),
        "total_steps": sum(steps),
        "mean_steps": round(statistics.mean(steps), 3) if steps else 0.0,
        "assistant_steps": asst,
        "tool_steps": tool,
        "records_with_state_transition": has_state_rem,
        "records_with_canonical_fix": has_fix,
        "records_with_evidence": has_evidence,
    }


def run(inp: str, outdir: str) -> Dict[str, Any]:
    os.makedirs(outdir, exist_ok=True)
    recs = _read_jsonl(inp)
    report: Dict[str, Any] = {"input": inp, "n_input": len(recs), "variants": {}}
    for variant in fa.VARIANTS:
        outs = [fa.apply_variant(r, variant) for r in recs]
        out_path = os.path.join(outdir, f"{variant}.jsonl")
        with open(out_path, "w") as f:
            for o in outs:
                f.write(json.dumps(o) + "\n")
        report["variants"][variant] = {
            "out": out_path,
            "stats": variant_stats(outs),
        }
    report["blocker"] = (
        "Model train/eval per variant is blocked: real FIREBALL D&D corpus and "
        "fireball-trained slug are not in the repo (see P7_fireball_status.md, E2). "
        "Data-transform layer is complete and tested."
    )
    return report


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--outdir", default="./_variants")
    ap.add_argument("--report", default=None, help="optional path to write the JSON report")
    args = ap.parse_args(argv)
    report = run(args.inp, args.outdir)
    text = json.dumps(report, indent=2)
    print(text)
    if args.report:
        with open(args.report, "w") as f:
            f.write(text + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
