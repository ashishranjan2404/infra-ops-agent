#!/usr/bin/env python3
"""Convert FIREBALL combat-turn records into our trajectory format.

Our trajectories (cf. opensre-traj/out/hud_trajectories.jsonl) are flat,
one-JSON-line-per-record with a stable id, a textual observation, the action(s)
taken, the tool/automation result, and a gold target answer. FIREBALL turns map
onto this cleanly:

    observation  <- before_utterances + combat_state_before (the table state +
                    what players just said)
    actions      <- commands_norm (the Avrae bot commands = the policy's action)
    tools_used   <- the command verbs (!cast, !attack, ...) — analogous to the
                    tool list we track for SRE agents
    result       <- automation_results (deterministic bot resolution)
    target       <- after_utterances (the human DM/player narration of the
                    outcome) — the gold continuation to predict / score against
    next_observation <- combat_state_after

A stable `trace_id` is the sha1 of (speaker_id + commands + before_state_idx),
so re-runs are deterministic and de-dupable.

Usage:
    python fireball_convert.py data/fireball_raw/*.jsonl -o data/fireball_traj.jsonl
    # programmatic:
    from fireball_convert import convert_row, convert_file
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable, Iterator

try:  # allow running as a script OR importing
    from fireball_schema import COMBATANT_KEYS, validate_row
except ImportError:  # pragma: no cover
    from .fireball_schema import COMBATANT_KEYS, validate_row  # type: ignore

SCHEMA_VERSION = "fireball-traj-v1"


def _combatant_line(c: dict) -> str:
    parts = [str(c.get(k, "")) for k in COMBATANT_KEYS]
    name, hp, cls, race, attacks, effects = parts
    s = f"{name} [{hp}]"
    if race:
        s += f" {race}"
    if cls:
        s += f" ({cls})"
    if effects:
        s += f" effects={effects}"
    return s


def _render_state(state: list) -> str:
    if not isinstance(state, list):
        return ""
    return "\n".join(_combatant_line(c) for c in state if isinstance(c, dict))


def _tool_verbs(commands: list) -> list[str]:
    """Extract Avrae command verbs, e.g. '!cast armor -t nim' -> 'cast'."""
    verbs: list[str] = []
    for cmd in commands:
        if not isinstance(cmd, str):
            continue
        tok = cmd.strip().lstrip("!").split()
        if tok:
            v = tok[0]
            if v not in verbs:
                verbs.append(v)
    return verbs


def make_trace_id(row: dict) -> str:
    key = "|".join([
        str(row.get("speaker_id", "")),
        "::".join(map(str, row.get("commands_norm", []))),
        str(row.get("before_state_idx", "")),
    ])
    return hashlib.sha1(key.encode("utf-8")).hexdigest()


def convert_row(row: dict, source: str = "fireball") -> dict:
    """Map ONE FIREBALL row to our trajectory record. Raises ValueError on
    schema problems so a bad shard fails loudly rather than silently dropping."""
    problems = validate_row(row)
    if problems:
        raise ValueError("invalid FIREBALL row: " + "; ".join(problems))

    before = list(row.get("before_utterances", []))
    commands = list(row.get("commands_norm", []))
    results = list(row.get("automation_results", []))
    after = list(row.get("after_utterances", []))

    observation = (
        "## Combat state\n" + _render_state(row.get("combat_state_before", []))
        + "\n\n## Recent dialogue\n" + "\n".join(map(str, before))
    )

    return {
        "schema": SCHEMA_VERSION,
        "trace_id": make_trace_id(row),
        "scenario_id": f"fireball-{make_trace_id(row)[:12]}",
        "source": source,
        "speaker_id": row.get("speaker_id"),
        "observation": observation,
        "actions": commands,            # the policy action(s)
        "tools_used": _tool_verbs(commands),
        "n_tool_calls": len(commands),
        "result": "\n".join(map(str, results)),   # deterministic bot resolution
        "target": "\n".join(map(str, after)),     # gold narration to predict
        "next_observation": "## Combat state\n" + _render_state(
            row.get("combat_state_after", [])),
        "utterance_history": list(row.get("utterance_history", [])),
        # provenance kept for traceability back to the source dataset
        "provenance": {
            "before_state_idx": row.get("before_state_idx"),
            "after_state_idx": row.get("after_state_idx"),
            "command_idxs": row.get("command_idxs"),
        },
    }


def convert_file(paths: Iterable[Path], skip_empty: bool = True
                 ) -> Iterator[dict]:
    """Yield converted records from one or more shard files. Rows whose action
    OR target is empty are skipped when skip_empty (not useful for training)."""
    for p in paths:
        with open(p) as fh:
            for ln, line in enumerate(fh):
                line = line.strip()
                if not line:
                    continue
                row = json.loads(line)
                rec = convert_row(row)
                if skip_empty and (not rec["actions"] or not rec["target"]):
                    continue
                yield rec


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("inputs", nargs="+", type=Path, help="FIREBALL .jsonl shards")
    ap.add_argument("-o", "--out", type=Path, required=True)
    ap.add_argument("--keep-empty", action="store_true")
    a = ap.parse_args()
    n = 0
    a.out.parent.mkdir(parents=True, exist_ok=True)
    with open(a.out, "w") as out:
        for rec in convert_file(a.inputs, skip_empty=not a.keep_empty):
            out.write(json.dumps(rec) + "\n")
            n += 1
    print(f"wrote {n} trajectory records -> {a.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
