"""
Domain-agnostic trajectory adapter (E7).

Goal: test transfer of REx-style diagnose-then-act policies from the SRE
incident domain to OTHER interactive game domains (text adventures): TextWorld,
Jericho (Z-machine IF), ALFWorld (embodied/text-aligned). All of these are
sequential, partially-observed, tool/command-driven environments — the same
shape as an SRE incident loop (observe -> hypothesize -> act -> resolve).

This module defines a SINGLE canonical trajectory schema (`CanonicalTrajectory`)
and pluggable per-domain adapters that normalize raw episode logs into it. The
canonical schema deliberately mirrors the fields the REx scoring stack already
consumes (a stated cause / goal, a gold target, distractors / red herrings, an
ordered action list, a success flag) so that downstream eval harnesses
(`rex/scoring.py`, `rex/eval_pass_at_k.py`) can score game episodes with ZERO
changes to shared core files.

Mapping intuition (game  ->  SRE analogue):
    observation text            -> alert / metric / log observation
    available_commands / tools  -> diagnostic + remediation tools
    the winning goal / quest    -> root_cause + canonical_fix
    losing / dead-end branches  -> trap_actions / red_herrings
    final 'you have won'        -> fix_resolves assertion

No third-party deps; pure stdlib so it runs under Python 3.13 with no install.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Callable, Iterable


# --------------------------------------------------------------------------- #
# Canonical schema
# --------------------------------------------------------------------------- #
@dataclass
class CanonicalStep:
    """One observe->act step of an interactive episode."""
    t: int
    observation: str            # what the agent saw (alert / room description)
    available_actions: list[str]  # tools / commands offered this step
    action: str                 # action the policy took
    reward: float = 0.0         # per-step reward if the env emits one


@dataclass
class CanonicalTrajectory:
    """
    Domain-agnostic episode. Field names chosen to line up with the SRE
    incident scenario schema so REx scoring can be reused verbatim.
    """
    episode_id: str
    domain: str                       # "textworld" | "jericho" | "alfworld" | "sre"
    goal: str                         # natural-language objective (== stated/gold target)
    gold_target: str                  # canonical solution string (== gold_root)
    distractors: list[str] = field(default_factory=list)  # red herrings / trap actions
    steps: list[CanonicalStep] = field(default_factory=list)
    solved: bool = False              # episode terminal success (== fix_resolves)
    final_answer: str = ""            # agent's stated conclusion (== stated_cause)
    meta: dict[str, Any] = field(default_factory=dict)

    # ---- convenience views used by SRE scoring -------------------------- #
    @property
    def actions(self) -> list[str]:
        return [s.action for s in self.steps]

    def to_sre_scoring_inputs(self) -> dict[str, Any]:
        """
        Project into the exact kwargs rex/scoring.deterministic_judge expects:
            deterministic_judge(stated_cause, gold_root, red_herrings)
        `final_answer` falls back to `goal` if the policy never stated one.
        """
        return {
            "stated_cause": self.final_answer or self.goal,
            "gold_root": self.gold_target,
            "red_herrings": list(self.distractors),
        }

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        return d


# --------------------------------------------------------------------------- #
# Adapter protocol
# --------------------------------------------------------------------------- #
# An adapter is just a function: raw_episode(dict) -> CanonicalTrajectory.
Adapter = Callable[[dict[str, Any]], CanonicalTrajectory]

_REGISTRY: dict[str, Adapter] = {}


def register(domain: str) -> Callable[[Adapter], Adapter]:
    def _wrap(fn: Adapter) -> Adapter:
        _REGISTRY[domain] = fn
        return fn
    return _wrap


def adapt(domain: str, raw: dict[str, Any]) -> CanonicalTrajectory:
    if domain not in _REGISTRY:
        raise KeyError(
            f"no adapter registered for domain {domain!r}; "
            f"have {sorted(_REGISTRY)}"
        )
    traj = _REGISTRY[domain](raw)
    _validate(traj)
    return traj


def adapt_many(domain: str, raws: Iterable[dict[str, Any]]) -> list[CanonicalTrajectory]:
    return [adapt(domain, r) for r in raws]


def _validate(t: CanonicalTrajectory) -> None:
    if not t.episode_id:
        raise ValueError("episode_id is required")
    if not t.gold_target:
        raise ValueError(f"{t.episode_id}: gold_target is required for scoring")
    for i, s in enumerate(t.steps):
        if s.t != i:
            raise ValueError(f"{t.episode_id}: step index mismatch at {i} (t={s.t})")
        if s.action and s.available_actions and s.action not in s.available_actions:
            # not fatal (env may allow free-form), but record it
            t.meta.setdefault("warnings", []).append(
                f"step {i}: action {s.action!r} not in available_actions"
            )


# --------------------------------------------------------------------------- #
# Per-domain adapters
# --------------------------------------------------------------------------- #
def _coerce_steps(raw_steps: list[dict[str, Any]],
                  obs_key: str, act_key: str,
                  avail_key: str, rew_key: str) -> list[CanonicalStep]:
    out: list[CanonicalStep] = []
    for i, rs in enumerate(raw_steps or []):
        out.append(CanonicalStep(
            t=i,
            observation=str(rs.get(obs_key, "")),
            available_actions=list(rs.get(avail_key, []) or []),
            action=str(rs.get(act_key, "")),
            reward=float(rs.get(rew_key, 0.0) or 0.0),
        ))
    return out


@register("textworld")
def adapt_textworld(raw: dict[str, Any]) -> CanonicalTrajectory:
    """
    TextWorld episode log. Microsoft TextWorld exposes per-step:
      `feedback`/`description` (obs), `admissible_commands`, the chosen `command`,
      and a scalar `score`. The quest goal is in `objective`.
    """
    steps = _coerce_steps(
        raw.get("transitions", []),
        obs_key="feedback", act_key="command",
        avail_key="admissible_commands", rew_key="score_delta",
    )
    return CanonicalTrajectory(
        episode_id=str(raw.get("game_id") or raw.get("episode_id") or "tw-?"),
        domain="textworld",
        goal=str(raw.get("objective", "")),
        gold_target=str(raw.get("walkthrough_goal") or raw.get("objective", "")),
        distractors=list(raw.get("losing_commands", []) or []),
        steps=steps,
        solved=bool(raw.get("won", False)),
        final_answer=str(raw.get("agent_summary", "")),
        meta={"max_score": raw.get("max_score"), "source": "TextWorld"},
    )


@register("jericho")
def adapt_jericho(raw: dict[str, Any]) -> CanonicalTrajectory:
    """
    Jericho (Z-machine interactive fiction, e.g. Zork) episode log. Jericho
    gives per-step `observation`, `valid_actions` (from world-model handicap),
    `action`, and `moves`/`score`. The gold is the optimal walkthrough action
    sequence summary.
    """
    steps = _coerce_steps(
        raw.get("history", []),
        obs_key="observation", act_key="action",
        avail_key="valid_actions", rew_key="reward",
    )
    return CanonicalTrajectory(
        episode_id=str(raw.get("rom") or raw.get("episode_id") or "jericho-?"),
        domain="jericho",
        goal=str(raw.get("goal", "complete the game")),
        gold_target=str(raw.get("walkthrough_summary") or raw.get("goal", "")),
        distractors=list(raw.get("dead_end_actions", []) or []),
        steps=steps,
        solved=bool(raw.get("victory", False)),
        final_answer=str(raw.get("agent_summary", "")),
        meta={"max_score": raw.get("max_score"), "source": "Jericho"},
    )


@register("alfworld")
def adapt_alfworld(raw: dict[str, Any]) -> CanonicalTrajectory:
    """
    ALFWorld episode log (text-aligned embodied tasks). Per-step it provides the
    textual `obs`, the admissible `actions`, the chosen `action`, and a
    terminal `goal_condition_success`. Task type is e.g. "pick_and_place".
    """
    steps = _coerce_steps(
        raw.get("trajectory", []),
        obs_key="obs", act_key="action",
        avail_key="admissible_actions", rew_key="reward",
    )
    return CanonicalTrajectory(
        episode_id=str(raw.get("task_id") or raw.get("episode_id") or "alf-?"),
        domain="alfworld",
        goal=str(raw.get("task_desc", "")),
        gold_target=str(raw.get("expert_plan_summary") or raw.get("task_desc", "")),
        distractors=list(raw.get("irrelevant_objects", []) or []),
        steps=steps,
        solved=bool(raw.get("goal_condition_success", False)),
        final_answer=str(raw.get("agent_summary", "")),
        meta={"task_type": raw.get("task_type"), "source": "ALFWorld"},
    )


@register("sre")
def adapt_sre(raw: dict[str, Any]) -> CanonicalTrajectory:
    """
    Reference adapter for the project's OWN domain — proves the schema is a true
    superset. Accepts a hud_trajectories.jsonl-style record OR a cidg scenario+run.
    """
    tools = raw.get("tools_used", []) or []
    steps = [
        CanonicalStep(t=i, observation="", available_actions=tools, action=tool)
        for i, tool in enumerate(tools)
    ]
    return CanonicalTrajectory(
        episode_id=str(raw.get("scenario_id") or raw.get("trace_id") or "sre-?"),
        domain="sre",
        goal="diagnose and remediate the incident root cause",
        gold_target=str(raw.get("gold_root") or raw.get("scenario_id", "")),
        distractors=list(raw.get("red_herrings", []) or []),
        steps=steps,
        solved=bool(raw.get("reward", 0) and float(raw.get("reward", 0)) >= 0.5),
        final_answer=str(raw.get("answer", "")),
        meta={"reward": raw.get("reward"), "source": "SRE/REx"},
    )


def registered_domains() -> list[str]:
    return sorted(_REGISTRY)


if __name__ == "__main__":
    import json
    import sys
    print("registered domains:", registered_domains(), file=sys.stderr)
    # tiny smoke demo
    demo = {
        "game_id": "tw-demo",
        "objective": "find the key and open the chest",
        "walkthrough_goal": "open chest with brass key",
        "losing_commands": ["eat key", "go north into lava"],
        "won": True,
        "agent_summary": "opened the chest using the brass key",
        "transitions": [
            {"feedback": "You are in a damp cellar.",
             "admissible_commands": ["take key", "go north"],
             "command": "take key", "score_delta": 1},
            {"feedback": "You hold a brass key.",
             "admissible_commands": ["open chest", "go north"],
             "command": "open chest", "score_delta": 1},
        ],
    }
    t = adapt("textworld", demo)
    print(json.dumps(t.to_dict(), indent=2))
    print("scoring inputs:", t.to_sre_scoring_inputs())
