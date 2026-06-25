"""Fireball (D&D actual-play) -> SRE-incident training-format adapter.

Task D8 / Claim 2. The FIREBALL dataset (Zhou et al., EMNLP 2022,
"FIREBALL: A Dataset of Dungeons and Dragons Actual-Play with Structured Game
State Information") records play-by-post combat as a stream of structured
triples:

    state_before  ->  command/utterance  ->  state_after

The Claim-2 thesis is that this (state -> action -> state') structure is the
SAME shape as an SRE incident-diagnosis trajectory (an agent observes cluster
state, issues a diagnostic/remediation action, observes the new state), so
supervised fine-tuning on FIREBALL transfers to multi-hop/cascade incidents.

This adapter converts one FIREBALL combat turn into a single training example
in the project's existing trajectory training format (the same shape consumed
by opensre-traj/train_rft*.py: a messages list with a graded `reward`, plus
provenance metadata).

BLOCKER (see 09_critique.md / SUMMARY.md): the REAL FIREBALL corpus is NOT in
the repo yet — it is blocked on Wenji pushing the data. This adapter is built
and unit-tested against a tiny SYNTHETIC fixture (fireball_fixture.jsonl) that
mimics the published FIREBALL schema. NO real Fireball training results are
produced or claimed here. When the real data lands, point `--in` at it.

Published FIREBALL record (subset of fields we rely on; see the HF dataset
`lara-martin/FIREBALL` / the paper's appendix):
    {
      "combat_id": str,
      "speaker_id": str,
      "before_utterances": [str, ...],   # narration before the command
      "commands": [str, ...],            # the Avrae bot command(s) issued
      "after_utterances": [str, ...],    # narration after
      "before_state": [ {actor...}, ... ],   # structured combat state
      "after_state":  [ {actor...}, ... ],
      "automation_results": str,         # mechanical result of the command
      "caster_after": {...}, "targets_after": [...]
    }

We are deliberately conservative: only the fields above are read, each is
optional, and a record missing the load-bearing fields is skipped (counted) so
a schema drift in the real dump fails loud-but-recoverable rather than silently
emitting garbage.
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from typing import Any, Iterable, Iterator


# --- training-format target -------------------------------------------------
# Mirrors the (state_before -> action -> state_after) example the project's
# trainer consumes: a chat `messages` list + a scalar `reward` + provenance.

SYSTEM_PROMPT = (
    "You are an agent that reasons over structured state transitions. "
    "Given the state before an action and the action taken, predict and "
    "justify the resulting state. This mirrors diagnosing how an action "
    "moves a system from one state to the next."
)


@dataclass
class TrainingExample:
    messages: list[dict[str, str]]
    reward: float
    meta: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> dict[str, Any]:
        return {"messages": self.messages, "reward": self.reward, "meta": self.meta}


# --- helpers ----------------------------------------------------------------

def _join(xs: Any, sep: str = " ") -> str:
    if xs is None:
        return ""
    if isinstance(xs, str):
        return xs.strip()
    if isinstance(xs, (list, tuple)):
        return sep.join(str(x).strip() for x in xs if str(x).strip())
    return str(xs).strip()


def _fmt_state(state: Any) -> str:
    """Render a FIREBALL combat state (list of actor dicts) compactly."""
    if not state:
        return "(empty)"
    if isinstance(state, str):
        return state.strip()
    parts = []
    for actor in state:
        if not isinstance(actor, dict):
            parts.append(str(actor))
            continue
        name = actor.get("name", actor.get("actor", "?"))
        hp = actor.get("hp", actor.get("current_hp"))
        seg = f"{name}"
        if hp is not None:
            seg += f"(hp={hp})"
        effects = actor.get("effects")
        if effects:
            seg += f"[{_join(effects, ',')}]"
        parts.append(seg)
    return "; ".join(parts)


def _reward_for(rec: dict[str, Any]) -> float:
    """Heuristic example-quality weight in [0,1].

    NOT a Fireball game score — it is a *data-quality / informativeness* weight
    so the trainer can down-weight degenerate turns (no state change, no
    command). Deliberately simple and documented; the real reward semantics for
    Claim-2 SFT are 'imitate well-formed transitions', so completeness == quality.
    """
    score = 0.0
    if _join(rec.get("commands")):
        score += 0.4
    if rec.get("before_state"):
        score += 0.2
    if rec.get("after_state"):
        score += 0.2
    # reward an actual observable state change (the transferable signal)
    if rec.get("before_state") and rec.get("after_state") \
            and rec.get("before_state") != rec.get("after_state"):
        score += 0.2
    return round(min(score, 1.0), 4)


# --- core -------------------------------------------------------------------

REQUIRED_ANY = ("commands",)            # a turn with no command is not a transition
REQUIRED_STATE = ("before_state", "after_state")


def adapt_record(rec: dict[str, Any]) -> TrainingExample | None:
    """Convert one FIREBALL record -> TrainingExample, or None if unusable."""
    if not isinstance(rec, dict):
        return None
    command = _join(rec.get("commands"))
    if not command:
        return None
    if not any(rec.get(k) for k in REQUIRED_STATE):
        return None

    before = _fmt_state(rec.get("before_state"))
    after = _fmt_state(rec.get("after_state"))
    narration_pre = _join(rec.get("before_utterances"))
    narration_post = _join(rec.get("after_utterances"))
    automation = _join(rec.get("automation_results"))

    user = (
        f"STATE_BEFORE: {before}\n"
        f"CONTEXT: {narration_pre or '(none)'}\n"
        f"ACTION: {command}"
    )
    assistant_parts = [f"RESULT: {automation or '(mechanical result not recorded)'}"]
    if narration_post:
        assistant_parts.append(f"NARRATION: {narration_post}")
    assistant_parts.append(f"STATE_AFTER: {after}")
    assistant = "\n".join(assistant_parts)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
        {"role": "assistant", "content": assistant},
    ]
    meta = {
        "source": "fireball",
        "combat_id": rec.get("combat_id"),
        "speaker_id": rec.get("speaker_id"),
        "state_changed": bool(
            rec.get("before_state")
            and rec.get("after_state")
            and rec.get("before_state") != rec.get("after_state")
        ),
    }
    return TrainingExample(messages=messages, reward=_reward_for(rec), meta=meta)


def adapt_stream(records: Iterable[dict[str, Any]]) -> Iterator[TrainingExample]:
    for rec in records:
        ex = adapt_record(rec)
        if ex is not None:
            yield ex


def _read_jsonl(path: str) -> Iterator[dict[str, Any]]:
    with open(path, "r", encoding="utf-8") as fh:
        for i, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as e:
                print(f"  [warn] skipping malformed line {i}: {e}", file=sys.stderr)


def convert_file(in_path: str, out_path: str) -> dict[str, int]:
    n_in = n_out = 0
    with open(out_path, "w", encoding="utf-8") as out:
        for rec in _read_jsonl(in_path):
            n_in += 1
            ex = adapt_record(rec)
            if ex is None:
                continue
            out.write(json.dumps(ex.to_json()) + "\n")
            n_out += 1
    return {"records_in": n_in, "examples_out": n_out, "skipped": n_in - n_out}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Fireball -> SRE training-format adapter")
    ap.add_argument("--in", dest="in_path", required=True,
                    help="FIREBALL jsonl (BLOCKED: real corpus pending from Wenji; "
                         "use fireball_fixture.jsonl to exercise the adapter)")
    ap.add_argument("--out", dest="out_path", required=True,
                    help="output training-format jsonl")
    args = ap.parse_args(argv)
    stats = convert_file(args.in_path, args.out_path)
    print(json.dumps(stats))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
