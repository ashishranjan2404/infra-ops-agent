#!/usr/bin/env python3
"""
E6 — Fireball ablation transforms: full vs state-only vs action-only.

A "Fireball trajectory" (the FIREBALL `state_before -> fix -> state_after`
shape, as mirrored by opensre-traj/SCHEMA.md) is a single SRE incident record
with a step-wise `trajectory` list interleaving:

  * assistant steps  -> {step, role:"assistant", thought, action:{tool,args}}
                        these carry the *policy decisions* (the ACTIONS).
  * tool steps        -> {step, role:"tool", name, result, evidence_ref}
                        these carry the *observed world* (the STATES).

plus a top-level `remediation` block holding the canonical fix and the
`state_before` / `state_after` numbers (the FIREBALL state transition).

This module defines three deterministic, pure transforms over that record so an
ablation can isolate *which channel of supervision matters*:

  full         : everything (control).
  state_only   : keep observations (tool results, evidence, state_before/after,
                 recovery_check) — DROP the agent's thoughts and tool calls.
                 Answers: "can a model learn from watching the world change,
                 with no demonstrated actions?"
  action_only  : keep the agent's thoughts + tool calls + canonical fix —
                 DROP all observed tool results / evidence / state numbers.
                 Answers: "can a model learn the action policy with no grounding
                 in what the actions produced?"

The transforms are the experimental artifact. Running them on REAL FIREBALL D&D
data is BLOCKED (see E2 / P7_fireball_status.md): that corpus is not in the repo.
The transforms are validated here on a synthetic fixture in the identical
schema (and run cleanly over the in-repo opensre-traj corpus, which uses the
same format) so they are ready the moment the data lands.

No fabricated results: this file produces *data variants*, not metrics.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from typing import Any, Dict, Iterable, List

VARIANTS = ("full", "state_only", "action_only")

# Keys on the remediation block that describe observed STATE (not the action).
_STATE_REMEDIATION_KEYS = (
    "primary_metric",
    "direction",
    "state_before",
    "state_after",
    "recovery_check",
    "resolved",
)
# Keys on the remediation block that describe the ACTION (the fix).
_ACTION_REMEDIATION_KEYS = (
    "fix_tool",
    "canonical_fix",
    "trust_tier",
)


def _is_assistant(step: Dict[str, Any]) -> bool:
    return step.get("role") == "assistant"


def _is_tool(step: Dict[str, Any]) -> bool:
    return step.get("role") == "tool"


def _validate_record(rec: Dict[str, Any]) -> None:
    if not isinstance(rec, dict):
        raise TypeError(f"record must be a dict, got {type(rec).__name__}")
    if "trajectory" not in rec or not isinstance(rec["trajectory"], list):
        raise ValueError("record missing list field 'trajectory'")
    for i, step in enumerate(rec["trajectory"]):
        if not isinstance(step, dict) or "role" not in step:
            raise ValueError(f"trajectory[{i}] is not a step dict with a 'role'")
        if step["role"] not in ("assistant", "tool"):
            raise ValueError(
                f"trajectory[{i}] has unknown role {step['role']!r} "
                "(expected 'assistant' or 'tool')"
            )


def transform_full(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Identity (deep copy) — the control condition."""
    _validate_record(rec)
    out = copy.deepcopy(rec)
    out["ablation"] = "full"
    return out


def transform_state_only(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Keep observations; drop the agent's thoughts and tool calls."""
    _validate_record(rec)
    out = copy.deepcopy(rec)
    out["trajectory"] = [s for s in out["trajectory"] if _is_tool(s)]
    rem = out.get("remediation")
    if isinstance(rem, dict):
        out["remediation"] = {k: v for k, v in rem.items() if k in _STATE_REMEDIATION_KEYS}
    # The gold action sequence is an action channel — drop it.
    if isinstance(out.get("answer"), dict):
        out["answer"] = {
            k: v
            for k, v in out["answer"].items()
            if k not in ("optimal_trajectory", "required_queries")
        }
    out["ablation"] = "state_only"
    return out


def transform_action_only(rec: Dict[str, Any]) -> Dict[str, Any]:
    """Keep the agent's thoughts + tool calls + canonical fix; drop observed state."""
    _validate_record(rec)
    out = copy.deepcopy(rec)
    new_traj: List[Dict[str, Any]] = []
    for s in out["trajectory"]:
        if _is_assistant(s):
            new_traj.append(s)
        # tool steps (observed results / evidence) are dropped entirely
    out["trajectory"] = new_traj
    rem = out.get("remediation")
    if isinstance(rem, dict):
        out["remediation"] = {k: v for k, v in rem.items() if k in _ACTION_REMEDIATION_KEYS}
    # Evidence is observed state — drop it.
    out.pop("evidence", None)
    out["ablation"] = "action_only"
    return out


_TRANSFORMS = {
    "full": transform_full,
    "state_only": transform_state_only,
    "action_only": transform_action_only,
}


def apply_variant(rec: Dict[str, Any], variant: str) -> Dict[str, Any]:
    if variant not in _TRANSFORMS:
        raise KeyError(f"unknown variant {variant!r}; expected one of {VARIANTS}")
    return _TRANSFORMS[variant](rec)


def transform_stream(records: Iterable[Dict[str, Any]], variant: str) -> Iterable[Dict[str, Any]]:
    for rec in records:
        yield apply_variant(rec, variant)


def _read_jsonl(path: str) -> List[Dict[str, Any]]:
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _write_jsonl(path: str, records: Iterable[Dict[str, Any]]) -> int:
    n = 0
    with open(path, "w") as f:
        for rec in records:
            f.write(json.dumps(rec) + "\n")
            n += 1
    return n


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Apply a Fireball ablation transform to a JSONL corpus.")
    ap.add_argument("--in", dest="inp", required=True, help="input trajectories.jsonl")
    ap.add_argument("--variant", choices=VARIANTS, required=True)
    ap.add_argument("--out", dest="out", required=True, help="output jsonl")
    args = ap.parse_args(argv)

    recs = _read_jsonl(args.inp)
    n = _write_jsonl(args.out, transform_stream(recs, args.variant))
    print(f"[fireball_ablate] {args.variant}: wrote {n} records -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
