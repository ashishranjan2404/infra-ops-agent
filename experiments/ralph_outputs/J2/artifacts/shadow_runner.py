#!/usr/bin/env python3
"""Shadow-mode incident runner (Task J2).

Run the SRE agent against a LIVE incident in *observe-only* mode: the agent reads
real telemetry, proposes a remediation PLAN, and the runner records the diagnosis —
but the runner GUARANTEES that no remediation (write) action is ever executed.

Grounding:
  - rex/loop.py     : propose()/parse_plan() — the agent's proposer (frozen LLM).
  - mreal/server.py : the live CIDG call-mesh exposes Prometheus /metrics; a fault
                      at one node cascades to its callers (gateway = loud victim).
  - tools_registry.json : read tools vs write (remediation) tools — the basis of the
                      shadow safety gate.

Safety model (the guarantee):
  Every proposed action is classified READ (observation) or WRITE (remediation).
  A ShadowExecutor *executes nothing*: it has no apply_action, no kubectl, no
  HTTP POST to /ctl, no sim mutation. It only LABELS each action with what WOULD
  have happened. Any attempt to actually mutate state raises ShadowViolation.
  See assert_no_side_effects() and the unit tests in test_shadow_runner.py.

Telemetry sources (pluggable; the agent code is identical across them):
  - PrometheusSource(base_url): scrape a live Prometheus / a mreal pod's /metrics.
  - FixtureSource(path)       : replay a recorded /metrics snapshot (offline / CI).
  This lets the harness run with NO live cluster (the documented blocker) while
  keeping the agent + safety path byte-identical to the live path.

This module deliberately does NOT import rex.harness.run_plan or sim.engine.apply_action:
shadow mode must be incapable of execution by construction, not merely by policy.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.request
from dataclasses import dataclass, field, asdict

# ----- write/read tool classification (shadow gate basis) -------------------

# Read (observation) tools may be "performed" in shadow mode because they have no
# side effect. Everything else is a remediation (write) tool and is NEVER executed.
READ_TOOLS = {
    "get_metrics", "get_logs", "get_events", "describe_pod",
    "get_deployment_status", "get_node_status", "query_traces", "get_alerts",
}
# Control verbs that are neither read nor remediation.
CONTROL_TOOLS = {"end_incident", "escalate_to_human"}


def _load_write_tools(repo: str) -> set[str]:
    try:
        reg = json.load(open(os.path.join(repo, "tools_registry.json")))
        names = {t["name"] for t in reg}
        return names - READ_TOOLS - CONTROL_TOOLS
    except (OSError, ValueError, KeyError):
        # Conservative fallback: treat any unknown tool as a write tool.
        return {"restart_pod", "increase_memory_limit", "scale_deployment",
                "rollback_deployment", "restart_service", "clear_cache",
                "drain_node", "cordon_node", "failover_service", "renew_certificate",
                "rotate_secret", "modify_network_policy", "delete_pvc",
                "scale_consumers", "rotate_logs"}


class ShadowViolation(RuntimeError):
    """Raised if shadow mode is ever asked to actually mutate live state."""


# ----- telemetry sources ----------------------------------------------------

class TelemetrySource:
    def fetch(self) -> str:
        raise NotImplementedError

    @staticmethod
    def parse_prometheus(text: str) -> dict:
        """Parse Prometheus text exposition into {metric{labels}: float}."""
        out: dict[str, float] = {}
        for line in (text or "").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            m = re.match(r"^(\S+?)\s+([-+0-9.eE]+|NaN|\+Inf|-Inf)$", line)
            if m:
                try:
                    out[m.group(1)] = float(m.group(2))
                except ValueError:
                    pass
        return out


@dataclass
class FixtureSource(TelemetrySource):
    """Replay a recorded /metrics snapshot — offline, no cluster needed."""
    path: str

    def fetch(self) -> str:
        with open(self.path) as f:
            return f.read()


@dataclass
class PrometheusSource(TelemetrySource):
    """Scrape a live Prometheus or an mreal pod's /metrics endpoint (READ-ONLY)."""
    base_url: str
    timeout: float = 3.0

    def fetch(self) -> str:
        url = self.base_url.rstrip("/") + "/metrics"
        with urllib.request.urlopen(url, timeout=self.timeout) as r:  # GET only
            return r.read().decode()


# ----- observation: derive an incident signal from telemetry ----------------

@dataclass
class Observation:
    raw_metrics: dict
    error_rate: dict          # app -> 5xx fraction
    cascade_victims: list     # apps with elevated errors (loud symptoms)
    summary: str


def observe(source: TelemetrySource) -> Observation:
    text = source.fetch()
    metrics = TelemetrySource.parse_prometheus(text)
    # aggregate app_requests_total{app=..,status=..} into per-app error rate
    by_app: dict[str, dict] = {}
    pat = re.compile(r'app_requests_total\{app="([^"]+)",status="(\d+)"\}')
    for k, v in metrics.items():
        m = pat.match(k)
        if m:
            app, status = m.group(1), m.group(2)
            d = by_app.setdefault(app, {"2xx": 0.0, "5xx": 0.0})
            d["5xx" if status.startswith("5") else "2xx"] += v
    err = {}
    for app, d in by_app.items():
        tot = d["2xx"] + d["5xx"]
        err[app] = round(d["5xx"] / tot, 4) if tot else 0.0
    victims = sorted([a for a, e in err.items() if e > 0.05], key=lambda a: -err[a])
    summary = (f"{len(victims)} service(s) over 5% error: "
               + ", ".join(f"{a}={err[a]:.0%}" for a in victims)) if victims \
        else "all services nominal"
    return Observation(raw_metrics=metrics, error_rate=err,
                       cascade_victims=victims, summary=summary)


# ----- the shadow executor (executes NOTHING) -------------------------------

@dataclass
class ShadowAction:
    tool: str
    args: dict
    classification: str       # "read" | "write" | "control" | "unknown"
    executed: bool            # ALWAYS False for write/control in shadow mode
    note: str


class ShadowExecutor:
    """Classifies a plan's actions and records what WOULD happen. Never mutates."""

    def __init__(self, repo: str):
        self.write_tools = _load_write_tools(repo)

    def classify(self, tool: str) -> str:
        if tool in READ_TOOLS:
            return "read"
        if tool in CONTROL_TOOLS:
            return "control"
        if tool in self.write_tools:
            return "write"
        return "unknown"   # unknown -> treated as write (never executed)

    def shadow_dispatch(self, plan: dict) -> list[ShadowAction]:
        out = []
        for a in plan.get("actions", []):
            tool = a.get("tool", "")
            cls = self.classify(tool)
            if cls == "read":
                note = "observation tool — safe; not executed in shadow mode either"
                executed = False
            else:
                note = ("REMEDIATION PROPOSED — NOT EXECUTED (shadow mode). "
                        "Would mutate live state on apply.")
                executed = False
            out.append(ShadowAction(tool=tool, args=a.get("args", {}) or {},
                                    classification=cls, executed=executed, note=note))
        return out


def assert_no_side_effects(actions: list[ShadowAction]) -> None:
    """The safety guarantee, checked: not a single action was executed."""
    bad = [a for a in actions if a.executed]
    if bad:
        raise ShadowViolation(
            f"shadow mode executed {len(bad)} action(s): "
            + ", ".join(a.tool for a in bad))


# ----- the runner -----------------------------------------------------------

@dataclass
class ShadowReport:
    incident: str
    started_at: float
    observation: dict
    stated_root_cause: str
    proposed_actions: list           # list[ShadowAction as dict]
    executed_count: int              # MUST be 0
    safety_guarantee: str
    blocker: str | None = None


def run_shadow(incident_name: str, source: TelemetrySource,
               propose_fn, repo: str | None = None) -> ShadowReport:
    """Observe -> propose -> classify -> record. Executes nothing.

    propose_fn(observation) -> plan dict {"root_cause":..., "actions":[...]}.
    Decoupled from rex.loop.propose so the runner is testable with a stub proposer
    and so live-LLM access is optional (documented blocker).
    """
    repo = repo or os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    obs = observe(source)
    plan = propose_fn(obs)
    execu = ShadowExecutor(repo)
    shadow_actions = execu.shadow_dispatch(plan)
    assert_no_side_effects(shadow_actions)   # hard guarantee
    return ShadowReport(
        incident=incident_name,
        started_at=time.time(),
        observation=asdict(obs),
        stated_root_cause=plan.get("root_cause", ""),
        proposed_actions=[asdict(a) for a in shadow_actions],
        executed_count=sum(1 for a in shadow_actions if a.executed),
        safety_guarantee=("0 actions executed. Shadow mode has no apply_action / "
                          "kubectl / control-POST path; remediation is recorded, not run."),
    )


def adapt_rex_propose(repo: str):
    """Wrap rex.loop.propose so it accepts an Observation. Requires a live LLM key.

    Builds a minimal text scenario from the observation so the existing frozen-model
    proposer can be reused unchanged. If agent.llm.call cannot reach a model, the
    caller should fall back to a stub proposer (documented live-LLM blocker).
    """
    def _propose(obs: Observation) -> dict:
        from rex.loop import build_prompt, parse_plan  # noqa: local import

        class _Scn:
            fault_node = (obs.cascade_victims[0] if obs.cascade_victims else "unknown")
            prompt_text = (
                "LIVE INCIDENT (shadow/observe-only). Real telemetry:\n"
                f"  {obs.summary}\n"
                f"  per-app error rate: {json.dumps(obs.error_rate)}\n"
                "Diagnose the ROOT cause (loud victims may be downstream) and propose "
                "a remediation plan. NOTE: nothing you propose will be executed.")
        from agent.llm import call
        text = call("claude-haiku-4-5", build_prompt(_Scn()), max_tokens=600)
        return parse_plan(text)
    return _propose


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Shadow-mode incident runner (observe-only)")
    p.add_argument("--incident", default="cidg-mreal")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--prometheus", help="base URL of live Prometheus/mreal pod")
    src.add_argument("--fixture", help="path to recorded /metrics snapshot")
    p.add_argument("--live-llm", action="store_true",
                   help="use the real frozen-model proposer (needs an LLM key)")
    args = p.parse_args()

    source = (PrometheusSource(args.prometheus) if args.prometheus
              else FixtureSource(args.fixture))
    repo = os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__)))))

    if args.live_llm:
        propose = adapt_rex_propose(repo)
    else:
        def propose(obs):  # offline stub proposer (no LLM key needed)
            root = (f"{obs.cascade_victims[-1]} appears to be the upstream root; "
                    "louder victims are downstream") if obs.cascade_victims \
                else "no active incident"
            acts = ([{"tool": "rollback_deployment",
                      "args": {"target": obs.cascade_victims[-1]}}]
                    if obs.cascade_victims else [])
            return {"root_cause": root, "actions": acts}

    report = run_shadow(args.incident, source, propose, repo)
    print(json.dumps(asdict(report), indent=2))
