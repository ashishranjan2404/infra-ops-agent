#!/usr/bin/env python3
"""SREGym-shaped environment adapter over our CIDG sim engine (task G2).

GOAL (reverse comparison): make OUR benchmark (sim/engine.py scenarios) look like a
SREGym environment so that an *external* SREGym-registered agent — in particular
SREGym's reference **Stratus** agent — could drive our scenarios through the same
5 tool families SREGym exposes:

    Metrics (Prometheus) | Logs (Loki) | Traces (Jaeger) |
    Cluster control (kubectl) | Submission (diagnosis + mitigation)

We back each family with `sim.engine.World` / `sim.engine.apply_action` /
`sim.engine.is_resolved`. The action space is our closed 25-tool registry
(tools_registry.json); cluster_control ALSO accepts free-form `kubectl`-style strings
and best-effort translates them, counting untranslatable calls as the fidelity gap.

This file is a self-contained SCAFFOLD. It is NOT the real SREGym MCP bundle and it does
NOT run Stratus (see RUN_PLAN.md for the blocker). It is fully runnable in-process and is
exercised by stub_agent.py + test_adapter.py.

NOTE: stdlib + pyyaml + our sim only. No new pip deps. Reads only; no shared-core edits.
"""
from __future__ import annotations

import os
import re
import sys

# --- locate repo root so we can import the real sim engine (read-only) -------------
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.abspath(os.path.join(_HERE, "..", "..", "..", ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from sim.engine import World, apply_action, is_resolved  # noqa: E402
from sim.spec import Action, load_spec                    # noqa: E402

# kind -> keywords a correct NL diagnosis should mention (stand-in for the LLM judge)
_KIND_KEYWORDS = {
    "mem_leak": ["memory", "leak", "oom", "rss", "limit"],
    "cpu_starve": ["cpu", "saturat", "throttl", "starv"],
    "disk_fill": ["disk", "full", "log", "space"],
    "pool_leak": ["pool", "connection", "leak", "exhaust"],
    "fd_exhaust": ["file descriptor", "fd", "exhaust", "limit"],
    "thread_exhaust": ["thread", "exhaust", "limit"],
    "bad_revision": ["deploy", "revision", "rollout", "rollback", "regression"],
    "bad_content": ["deploy", "content", "config", "rollback"],
    "config_bloat": ["config", "policy", "bloat", "control plane"],
    "cert_expire": ["cert", "tls", "expire", "renew"],
    "cache_flush": ["cache", "flush", "cold", "miss"],
    "node_notready": ["node", "notready", "not ready", "drain", "cordon"],
    "net_delay": ["network", "latency", "delay", "policy"],
    "dns_race": ["dns", "race", "resolve", "network"],
    "dep_revoked": ["dependency", "revoked", "quota", "permission", "failover"],
    "defense_amplify": ["defense", "amplif", "policy", "network"],
    "host_agent_crash": ["host", "agent", "crash", "rollback"],
}

# canonical remediation by kind (mirrors sim.engine.REMEDIATION — kept local so we don't
# import private engine state; used only by the stub's "solve" path, not for grading).
_CANONICAL_FIX = {
    "cpu_starve": "scale_deployment", "mem_leak": "increase_memory_limit",
    "pool_leak": "restart_service", "fd_exhaust": "restart_service",
    "thread_exhaust": "rollback_deployment", "churn_spike": "modify_network_policy",
    "config_bloat": "modify_network_policy", "bad_content": "rollback_deployment",
    "bad_revision": "rollback_deployment", "cert_expire": "renew_certificate",
    "cache_flush": "clear_cache", "disk_fill": "rotate_logs",
    "node_notready": "cordon_node", "net_delay": "modify_network_policy",
    "dns_race": "modify_network_policy", "dep_revoked": "failover_service",
    "defense_amplify": "modify_network_policy", "host_agent_crash": "rollback_deployment",
}

# kubectl verb -> our registry tool. READ verbs map to None (observation no-op).
_KUBECTL_MAP = {
    "scale": "scale_deployment",
    "drain": "drain_node",
    "cordon": "cordon_node",
    "uncordon": "cordon_node",
    "get": None, "describe": None, "logs": None, "top": None, "explain": None,
}


def _clean_target(tok: str) -> str:
    """Strip resource prefixes (deploy/, pod/...) and namespaces from a kubectl token."""
    tok = tok.split("=", 1)[0]                       # drop `=`-joined flag tails
    for pre in ("deployment/", "deploy/", "pod/", "po/", "node/", "svc/", "service/"):
        if tok.startswith(pre):
            return tok[len(pre):]
    return tok


def _parse_kubectl(command: str, node_names: set) -> tuple[str | None, str | None, bool]:
    """Best-effort translate a kubectl-style string into (tool, target, untranslated).

    untranslated=True means we could not map it to a real mutation in our 25-verb world
    (counted toward the fidelity gap). READ verbs translate to (None, target, False) — a
    legitimate observation no-op.
    """
    toks = command.replace("=", " = ").split()
    if not toks or toks[0] != "kubectl":
        return None, None, True
    # find the verb (first token after `kubectl`, skipping global flags like -n ns)
    verb = None
    rest = []
    skip_next = False
    for t in toks[1:]:
        if skip_next:
            skip_next = False
            continue
        if t in ("-n", "--namespace", "--context"):
            skip_next = True
            continue
        if t == "rollout":
            verb = "rollout"
            continue
        if verb is None:
            verb = t
            continue
        rest.append(t)
    # rollout undo/restart subcommands
    if verb == "rollout":
        sub = rest[0] if rest else ""
        tool = {"undo": "rollback_deployment", "restart": "restart_service"}.get(sub)
        target = _first_target(rest[1:], node_names)
        return (tool, target, tool is None)
    if verb == "delete" and rest and rest[0] in ("pod", "po", "pods"):
        return "restart_pod", _first_target(rest[1:], node_names), False
    if verb in _KUBECTL_MAP:
        tool = _KUBECTL_MAP[verb]
        target = _first_target(rest, node_names)
        # READ verbs (tool is None) are valid observation no-ops, not untranslated
        return tool, target, False
    return None, None, True                          # genuinely unmappable mutation


def _first_target(toks: list, node_names: set) -> str | None:
    for t in toks:
        if t.startswith("-") or t in ("=",):
            continue
        cand = _clean_target(t)
        if cand in node_names:
            return cand
    # fall back to first bare non-flag token even if it doesn't match a node
    for t in toks:
        if not t.startswith("-") and t not in ("=", "deployment", "deploy", "pod"):
            c = _clean_target(t)
            if c and not c.isdigit():
                return c
    return None


class SREGymEnv:
    """A single CIDG scenario presented through the SREGym tool surface."""

    def __init__(self, scenario_path: str, seed: int = 0):
        if not os.path.isabs(scenario_path):
            scenario_path = os.path.join(_REPO, scenario_path)
        self.path = scenario_path
        self.spec = load_spec(scenario_path)
        self.seed = seed
        self._node_names = {n.name for n in self.spec.nodes}
        rc = self.spec.root_cause
        self.fault_node = rc.location.split("->")[0].strip()
        self.kind = rc.kind
        self.world: World | None = None
        self.actions: list = []
        self._kubectl_calls = 0
        self._untranslated = 0

    # ---- lifecycle ----------------------------------------------------------------
    def reset(self) -> dict:
        self.world = World.from_spec(self.spec, inject=True)
        self.actions = []
        self._kubectl_calls = 0
        self._untranslated = 0
        return {
            "problem": (self.spec.meta.get("title")
                        or f"Incident on scenario {self.spec.id}: SLOs are breached."),
            "namespace": self.spec.id,
            "phases": ["diagnosis", "mitigation"],
            "nodes": sorted(self._node_names),
        }

    # ---- MCP family: Metrics (Prometheus stand-in) --------------------------------
    def get_metrics(self, node: str | None = None) -> dict:
        assert self.world, "call reset() first"
        out = {}
        for name in self._node_names:
            if node and name != node:
                continue
            out[name] = {
                "error_rate_pct": round(self.world.metric(name, "error_rate_pct"), 3),
                "p99_latency_ms": round(self.world.metric(name, "p99_latency_ms"), 3),
            }
        return out

    # ---- MCP family: Logs (Loki stand-in) -----------------------------------------
    def get_logs(self, node: str | None = None, query: str = "") -> list:
        lines = []
        for g in self.spec.observation.smoking_guns:
            if node and g.node != node:
                continue
            # bury the signature under noise lines (emergent loudness in our world)
            for i in range(max(0, g.buried_under)):
                lines.append(f"[{g.node}] INFO routine log line {i}")
            lines.append(f"[{g.node}] ERROR {g.signature}")
        if query:
            lines = [ln for ln in lines if query.lower() in ln.lower()]
        return lines

    # ---- MCP family: Traces (Jaeger stand-in; LOW FIDELITY) -----------------------
    def get_traces(self, node: str | None = None) -> dict:
        assert self.world, "call reset() first"
        spans = []
        for e in self.spec.edges:
            if node and node not in (e.src, e.dst):
                continue
            spans.append({"src": e.src, "dst": e.dst, "type": e.type,
                          "latency_ms": round(self.world.metric(e.dst, "p99_latency_ms"), 2)})
        return {"low_fidelity": True, "note": "edge-list approximation, NOT real Jaeger",
                "spans": spans}

    # ---- MCP family: Cluster control (kubectl stand-in) ---------------------------
    def cluster_control(self, command: str | None = None,
                        tool: str | None = None, args: dict | None = None) -> dict:
        assert self.world, "call reset() first"
        translated_from = None
        untranslated = False
        if command is not None:
            self._kubectl_calls += 1
            tool, target, untranslated = _parse_kubectl(command, self._node_names)
            translated_from = command
            args = {"target": target} if target else {}
            if untranslated:
                self._untranslated += 1
                return {"applied": False, "tool": None, "target": None,
                        "translated_from": translated_from, "untranslated": True,
                        "resolved": is_resolved(self.world)}
            if tool is None:                          # READ verb -> observation no-op
                return {"applied": False, "tool": None, "read_only": True,
                        "target": target, "translated_from": translated_from,
                        "untranslated": False, "resolved": is_resolved(self.world)}
        args = args or {}
        target = args.get("target")
        act = Action(tool=tool, args=args)
        self.actions.append({"tool": tool, "args": args})
        apply_action(self.world, act)
        return {"applied": True, "tool": tool, "target": target,
                "target_matched_node": target in self._node_names,
                "translated_from": translated_from, "untranslated": False,
                "resolved": is_resolved(self.world)}

    # ---- MCP family: Submission ---------------------------------------------------
    def submit_diagnosis(self, text: str) -> dict:
        t = (text or "").lower()
        node_ok = self.fault_node.lower() in t
        kws = _KIND_KEYWORDS.get(self.kind, [self.kind])
        kw_ok = any(k in t for k in kws)
        return {"diagnosis_correct": bool(node_ok and kw_ok),
                "gold_fault_node": self.fault_node, "gold_kind": self.kind,
                "node_mentioned": node_ok, "kind_keyword_found": kw_ok}

    def submit_mitigation(self) -> dict:
        assert self.world, "call reset() first"
        resolved = is_resolved(self.world)
        return {"resolved": bool(resolved),
                "root_cleared": bool(self.world.root_cleared),
                "actions": list(self.actions)}

    # ---- bookkeeping --------------------------------------------------------------
    def canonical_fix_tool(self) -> str | None:
        """The clean fix our engine accepts for this kind (stub convenience only)."""
        return _CANONICAL_FIX.get(self.kind)

    def fidelity(self) -> dict:
        rate = (self._untranslated / self._kubectl_calls) if self._kubectl_calls else 0.0
        return {"kubectl_calls": self._kubectl_calls,
                "untranslated_kubectl": self._untranslated,
                "untranslated_rate": round(rate, 3)}


if __name__ == "__main__":
    import argparse
    import json
    ap = argparse.ArgumentParser(description="Smoke-run the SREGym adapter on one scenario.")
    ap.add_argument("--scenario", default="scenarios/cidg/22-leaf-bad-deploy-positive.yaml")
    a = ap.parse_args()
    env = SREGymEnv(a.scenario)
    print(json.dumps(env.reset(), indent=2))
    print("metrics(fault):", json.dumps(env.get_metrics(env.fault_node)))
    print("logs:", env.get_logs())
    res = env.cluster_control(tool=env.canonical_fix_tool(), args={"target": env.fault_node})
    print("cluster_control:", json.dumps(res))
    print("mitigation:", json.dumps(env.submit_mitigation()))
    print("fidelity:", json.dumps(env.fidelity()))
