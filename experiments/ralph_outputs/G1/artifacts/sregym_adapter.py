#!/usr/bin/env python3
"""G1 adapter: drive OUR plan-policy agent through SREGym's problem/submission protocol.

SREGym (arXiv:2605.07161v1; github.com/SREGym/SREGym) runs an SRE agent against a LIVE
Kubernetes problem P=(E,I,F,O): the agent observes E via MCP interface I, submits a
natural-language DIAGNOSIS (graded by oracle O_d, a 9-question LLM checklist, tau=7/9),
then performs MITIGATION on the cluster and signals done (graded by O_m, a programmatic
recovery verifier). E2E = O_d AND O_m on the same run.

Our agent (rex.loop.propose / rex.tree) is a NON-INTERACTIVE planner: it emits one JSON
plan {"root_cause": str, "actions":[{"tool","args":{"target"}}]}. This adapter is the
body that SREGym's `--agent` registration would call. It:
  1. gathers a real observation bundle from the cluster (ObservationGatherer),
  2. builds a prompt FROM that bundle (not a leaked spec) and proposes a plan,
  3. turns the plan's root_cause into the O_d diagnosis string (originating component
     first, downstream services labeled as victims),
  4. translates each plan action into a kubectl/MCP command via action_translation.json,
     resolving logical targets to namespace/kind/name at run time (TargetResolver),
  5. reports out-of/partial-action-space and escalation honestly.

OFFLINE/DRY-RUN: importable and testable with NO cluster, NO Docker. The Stub* providers
let the contract be validated by test_sregym_adapter.py. A real run binds SREGymClient to
SREGym's BaseAgent submission API (see run_plan.md) and replaces the stubs.

DOES NOT import or mutate any shared rex/* core module at run time (the prompt is built
directly from the observation bundle). The default proposer lazily imports agent.llm only
when actually proposing against a live model.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Callable, Optional

try:                       # python<3.8 has no Protocol; we target 3.12 but stay defensive
    from typing import Protocol
except ImportError:        # pragma: no cover
    Protocol = object      # type: ignore

_HERE = os.path.dirname(os.path.abspath(__file__))
_TRANSLATION_PATH = os.path.join(_HERE, "action_translation.json")

ProposeFn = Callable[[Optional[object], Optional[str]], dict]


# --------------------------------------------------------------------------- #
# Provider protocols (SREGym binds these; Stub* implement them offline)         #
# --------------------------------------------------------------------------- #
class ObservationGatherer(Protocol):
    def gather(self, problem_id: str) -> dict: ...


class TargetResolver(Protocol):
    def resolve(self, logical_target: str) -> dict: ...


class SREGymClient(Protocol):
    # TODO(integration): bind to SREGym's real agent/submission API at install time.
    def submit_diagnosis(self, text: str) -> dict: ...
    def run_command(self, argv: list) -> dict: ...
    def signal_done(self) -> dict: ...


# --------------------------------------------------------------------------- #
# Offline stubs                                                                 #
# --------------------------------------------------------------------------- #
class StubGatherer:
    """A deterministic offline observation bundle so the contract is testable.
    A real gatherer issues Prometheus/Loki/Jaeger/kubectl queries via SREGym MCP."""

    def __init__(self, bundle: Optional[dict] = None):
        self._bundle = bundle or {
            "alert": "503 error-rate spike across product APIs (checkout, payments).",
            "metrics": {"checkout.error_rate_pct": 62, "payments.error_rate_pct": 57},
            "logs": ["checkout: 'request failed: 503 from api-gateway'"],
            "traces": [],
            "topology": [{"src": "checkout", "dst": "api-gateway", "type": "calls"}],
            "targets": ["checkout", "payments", "api-gateway"],
            "primary": "checkout",
        }

    def gather(self, problem_id: str) -> dict:
        return dict(self._bundle)


class StubResolver:
    """Resolve a logical target -> {namespace, kind, name}. A real resolver runs
    `kubectl get deploy,sts,node -A` and matches. Returns {} on unknown target."""

    def __init__(self, namespace: str = "default", known: Optional[set] = None):
        self._ns = namespace
        self._known = known  # None => resolve anything (offline convenience)

    def resolve(self, logical_target: str) -> dict:
        if not logical_target:
            return {}
        if self._known is not None and logical_target not in self._known:
            return {}
        return {"namespace": self._ns, "kind": "deployment", "name": logical_target}


# --------------------------------------------------------------------------- #
# Default proposer (lazy; only touches a live model when called)                #
# --------------------------------------------------------------------------- #
def _prompt_from_observation(obs: dict) -> str:
    """Build the proposer prompt directly from a gathered observation bundle — NOT from
    a leaked scenario spec (SREGym withholds the ground-truth structure on purpose)."""
    topo = "; ".join(f"{e['src']} --{e.get('type','calls')}--> {e['dst']}"
                     for e in obs.get("topology", []))
    lines = [
        "You are an SRE remediation agent. Diagnose the ROOT cause (it may be UPSTREAM of "
        "the loudest alert) and output a remediation PLAN.",
        f"Alert: {obs.get('alert','')}",
        f"Metrics: {json.dumps(obs.get('metrics', {}))}",
        f"Logs (sampled): {' | '.join(obs.get('logs', [])[:5])}",
        f"Topology: {topo}",
        f"Candidate targets: {', '.join(obs.get('targets', []))}",
        "",
        'Respond with ONLY JSON: {"root_cause":"<one sentence>",'
        '"actions":[{"tool":"<tool>","args":{"target":"<service>"}}]}',
    ]
    return "\n".join(lines)


def default_propose(model: str = "claude-haiku-4-5") -> ProposeFn:
    """A propose_fn closure over a model. Lazily imports agent.llm + rex.loop.parse_plan
    so importing this module needs no cluster, no API key, no network."""
    def _propose(observation, _feedback):
        from agent.llm import call            # lazy: only when actually proposing
        from rex.loop import parse_plan        # reuse the tolerant parser (read-only import)
        text = call(model, _prompt_from_observation(observation or {}), max_tokens=600)
        return parse_plan(text)
    return _propose


# --------------------------------------------------------------------------- #
# The adapter                                                                   #
# --------------------------------------------------------------------------- #
def load_translation(path: str = _TRANSLATION_PATH) -> dict:
    with open(path) as fh:
        return json.load(fh)["tools"]


@dataclass
class SREGymPlannerAdapter:
    propose_fn: ProposeFn
    gatherer: ObservationGatherer
    resolver: TargetResolver
    translation: dict = field(default_factory=load_translation)
    entry_kind: str = "non-interactive planner (transfer)"
    caveat: str = ("non-interactive planner; SREGym reference agents are interactive "
                   "MCP tool-users — this is a transfer/zero-shot result, not like-for-like")

    # ---- diagnosis ----
    def build_diagnosis(self, plan: dict, observation: Optional[dict] = None) -> str:
        root = (plan.get("root_cause") or "").strip()
        obs = observation or {}
        primary = obs.get("primary")
        victims = [t for t in obs.get("targets", []) if t != primary]
        text = root or "(no root cause stated)"
        if victims:
            text += (f" Originating/most-suspect component first; affected DOWNSTREAM "
                     f"services (victims, not root): {', '.join(victims)}.")
        return text

    # ---- action translation ----
    def translate_action(self, action: dict) -> dict:
        tool = action.get("tool", "")
        spec = self.translation.get(tool)
        if spec is None:
            return {"tool": tool, "expressible": False, "argv": None,
                    "reason": "unknown tool (not in our action space)"}
        if not spec.get("expressible"):
            return {"tool": tool, "expressible": False, "argv": None,
                    "reason": spec.get("reason", "no generic kubectl mapping")}
        target = (action.get("args") or {}).get("target", "")
        binding = self.resolver.resolve(target) if target else {}
        if not binding:
            return {"tool": tool, "expressible": False, "argv": None,
                    "reason": "unresolved target"}
        fill = {
            "ns": binding.get("namespace", "default"),
            "kind": binding.get("kind", "deployment"),
            "name": binding.get("name", target),
            "replicas": str((action.get("args") or {}).get("replicas", 3)),
            "mem": str((action.get("args") or {}).get("memory", "1Gi")),
        }
        # __MEM_PATCH__ is a sentinel: the JSON-patch body has literal {} braces that must
        # NOT pass through str.format. Substitute it directly after formatting the rest.
        mem_patch = ('[{"op":"replace","path":"/spec/template/spec/containers/0/'
                     'resources/limits/memory","value":"%s"}]' % fill["mem"])
        argv = [mem_patch if tok == "__MEM_PATCH__" else tok.format(**fill)
                for tok in spec["argv_template"]]
        return {"tool": tool, "expressible": True, "argv": argv, "reason": None}

    def translate_plan(self, plan: dict) -> dict:
        actions = plan.get("actions", []) or []
        commands, skipped = [], []
        for a in actions:
            t = self.translate_action(a)
            if t["expressible"]:
                commands.append(t["argv"])
            else:
                skipped.append({"action": a, "reason": t["reason"]})
        n = len(actions)
        return {
            "commands": commands,
            "skipped": skipped,
            "out_of_action_space": n > 0 and len(commands) == 0,
            "partial_action_space": len(commands) > 0 and len(skipped) > 0,
        }

    # ---- one problem ----
    def run_problem(self, problem_id: str, client: Optional[SREGymClient] = None,
                    dry_run: bool = True) -> dict:
        obs = self.gatherer.gather(problem_id)
        plan = self.propose_fn(obs, None)
        actions = plan.get("actions", []) or []
        escalated = len(actions) == 0
        diagnosis = self.build_diagnosis(plan, obs)
        tp = self.translate_plan(plan)

        submitted = False
        if not dry_run and client is not None:
            client.submit_diagnosis(diagnosis)
            for argv in tp["commands"]:
                client.run_command(argv)
            client.signal_done()
            submitted = True

        return {
            "problem_id": problem_id,
            "entry_kind": self.entry_kind,
            "observation_used": True,
            "diagnosis_text": diagnosis,
            "plan": plan,
            "commands": tp["commands"],
            "skipped": tp["skipped"],
            "out_of_action_space": tp["out_of_action_space"],
            "partial_action_space": tp["partial_action_space"],
            "escalated": escalated,
            "submitted": submitted,
            "dry_run": dry_run,
            "time_cost_measured": False,   # T-T-D / T-T-M / tokens not measured offline
            "caveat": self.caveat,
        }


def make_offline_adapter(stub_plan: Optional[dict] = None) -> SREGymPlannerAdapter:
    """Fully offline adapter: a canned proposer (no model call) for contract testing."""
    plan = stub_plan or {"root_cause": "checkout is OOMKilled; RSS exceeds memory limit",
                         "actions": [{"tool": "increase_memory_limit",
                                      "args": {"target": "checkout", "memory": "2Gi"}}]}
    return SREGymPlannerAdapter(
        propose_fn=lambda obs, fb: plan,
        gatherer=StubGatherer(),
        resolver=StubResolver(),
    )


if __name__ == "__main__":   # tiny offline dry-run demo
    a = make_offline_adapter()
    print(json.dumps(a.run_problem("demo-0001"), indent=2))
