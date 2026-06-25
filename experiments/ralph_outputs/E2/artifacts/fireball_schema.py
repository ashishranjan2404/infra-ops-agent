#!/usr/bin/env python3
"""Expected schema of one FIREBALL row, captured from a REAL sample.

Source: lara-martin/FIREBALL :: filtered/00068c6b03adc2c102756053cf6edd05.jsonl
(line 0), downloaded 2026-06 via huggingface_hub. FIREBALL = Zhu et al.,
"FIREBALL: A Dataset of Dungeons and Dragons Actual-Play with Structured Game
State Information", ACL 2023, arXiv:2305.01528.

Each JSON line is ONE combat "turn instance": the narration + game state
immediately *before* a sequence of Avrae bot commands, the commands themselves
(normalized), the bot's automation output, and the narration + game state
*after*. This is exactly a (state, action, result, next_state) tuple — i.e. a
single trajectory step.

REAL top-level keys (17), with observed types and meaning:

    speaker_id          str    anonymized Discord user id of the actor
    before_utterances   list[str]  player/DM chat lines preceding the action
    combat_state_before list[dict] each combatant's snapshot (name, hp, class,
                                   race, attacks, spells, actions, effects,
                                   description, controller); the OBSERVATION
    current_actor       dict|None  the combatant whose turn it is (may be null)
    commands_norm       list[str]  normalized Avrae commands, e.g. "!cast armor
                                   -t nim", "!attack greatsword" — the ACTION
    automation_results  list[str]  bot's resolved narration of the commands —
                                   the deterministic RESULT / tool output
    caster_after        dict   the acting combatant's state after the command
    targets_after       list[dict] targeted combatants' state after
    combat_state_after  list[dict] full combatant snapshot after — NEXT OBS
    after_utterances    list[str]  chat lines following (the human narration of
                                   what the command did) — the GOLD continuation
    utterance_history   list[str]  rolling "Player N: ..." dialogue context
    before_idxs         list[int]  source-message indices (provenance)
    before_state_idx    int        provenance index
    command_idxs        list[int]  provenance indices
    after_state_idx     int        provenance index
    after_idxs          list[int]  provenance indices
    embed_idxs          list[int]  provenance indices

A combatant snapshot (element of combat_state_before/after) looks like:
    {"name": "Vivi", "hp": "<48/48 HP; Healthy>", "class": null,
     "race": "Displacer Beast Kitten", "attacks": "Tentacles", "spells": "",
     "actions": null, "effects": "", "description": "...", "controller": "..."}

NOTE on naming: the task calls the target file "incidents.jsonl". FIREBALL ships
as 1475 `filtered/*.jsonl` shards (no single incidents.jsonl). We treat each
shard line as one record; see fireball_convert.py for the mapping to our format.
"""
from __future__ import annotations

# Required keys we rely on in the converter. Validation fails loudly if a row
# is missing any of these (schema drift guard).
REQUIRED_KEYS = (
    "speaker_id",
    "before_utterances",
    "combat_state_before",
    "commands_norm",
    "automation_results",
    "combat_state_after",
    "after_utterances",
    "utterance_history",
)

# Combatant snapshot keys we read (others ignored, kept in raw passthrough).
COMBATANT_KEYS = ("name", "hp", "class", "race", "attacks", "effects")


def validate_row(row: dict) -> list[str]:
    """Return a list of schema problems for one row (empty = valid)."""
    problems: list[str] = []
    if not isinstance(row, dict):
        return [f"row is {type(row).__name__}, expected dict"]
    for k in REQUIRED_KEYS:
        if k not in row:
            problems.append(f"missing key: {k}")
    for k in ("before_utterances", "commands_norm", "automation_results",
              "combat_state_before", "combat_state_after", "after_utterances"):
        if k in row and not isinstance(row[k], list):
            problems.append(f"key {k} is {type(row[k]).__name__}, expected list")
    return problems
