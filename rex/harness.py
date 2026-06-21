"""Phase-1 harness: load an incident as a self-consistent scenario, dispatch a
plan's tool-calls through the real Tier-A sim (sim/engine.py), gate each via
is_safe (Phase-1 STUB), and read whether the incident resolved.

Two scenarios:
  - oom_kill: the CIDG `21-leaf-oom` spec — EASY, non-hidden root (image-resizer).
  - gcp_service_control: the CIDG `01-gcp-service-control` cascade — HIDDEN root:
    the loud 503s land on product victims; the real root is the service-control
    control plane (buried NullPointer policy crash). Used for the diagnostic-climb probe.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field

from sim.engine import World, apply_action
from sim.spec import Action, ScenarioSpec, load_spec

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# root_cause.kind -> opensre-style category (the gold category for graded diagnosis)
_KIND_CATEGORY = {
    "mem_leak": "resource_exhaustion", "cpu_starve": "resource_exhaustion",
    "disk_fill": "resource_exhaustion", "pool_leak": "resource_exhaustion",
    "fd_exhaust": "resource_exhaustion", "thread_exhaust": "resource_exhaustion",
    "bad_revision": "bad_deploy", "bad_content": "bad_deploy",
    "config_bloat": "config_error", "cert_expire": "config_error",
    "net_delay": "network_fault", "dns_race": "network_fault",
    "node_notready": "node_failure", "cache_flush": "saturation",
    "churn_spike": "saturation", "dep_revoked": "dependency_failure",
}

_KIND_KEYWORDS = {
    "mem_leak": ["memory", "leak", "oom", "rss", "limit"],
    "config_bloat": ["config", "policy", "control plane", "crash"],
}

# Per-scenario config: spec path, diagnosis ground truth for the judge, and (where
# the spec's tool-reuse is ambiguous) explicit fix/trap overrides.
_SCENARIOS = {
    "oom_kill": {
        "path": "scenarios/cidg/21-leaf-oom-positive.yaml",
        "style": "leaf",
        "gold_root": ("a per-process memory leak on 'image-resizer': its RSS climbs past "
                      "the container memory limit and the kernel OOM-kills the pod"),
        "red_herrings": ["too few replicas / needs more scaling",
                         "a cache problem", "a bad deploy / image regression"],
    },
    "gcp_service_control": {
        "path": "scenarios/cidg/01-gcp-service-control.yaml",
        "style": "cascade",
        "gold_root": ("the 'service-control' control plane is crash-looping from a bad/blank "
                      "quota-policy config (NullPointer); the product 503s on workspace / "
                      "compute-api are DOWNSTREAM symptoms of that upstream control-plane failure"),
        "red_herrings": [
            "a product service (workspace, compute-api, or bigquery-api) being the root cause",
            "the api-gateway itself being the root",
            "the recent workspace deploy / a bad deploy on a product",
            "resource exhaustion on a product service",
            "just restarting or scaling service-control (that herds Spanner and worsens it)",
        ],
        "fix_tools": {"modify_network_policy"},                 # the clean root fix (disable bad path)
        "traps": [{"tool": "scale_deployment", "target": "service-control"}],  # herd -> Spanner
    },
}


@dataclass
class Scenario:
    name: str
    spec: ScenarioSpec
    fault_node: str
    kind: str
    category: str
    correct_fix_tools: set
    trap_actions: list                      # [{"tool": str, "target": str}]
    root_cause_keywords: list
    gold_root_description: str
    red_herring_hints: list
    prompt_text: str = field(repr=False)


def _build_leaf_prompt(spec: ScenarioSpec, fault_node: str) -> str:
    node = spec.node(fault_node)
    mem = node.resources.mem_limit_mb if node and node.resources.mem_limit_mb else "its"
    replicas = node.resources.replicas if node else "?"
    slo = "; ".join(f"{s.metric} {s.direction.replace('_', '-')} {s.threshold}" for s in spec.slo)
    return (
        f"ALERT firing on service '{fault_node}'.\n"
        f"Symptoms: the pod is being OOMKilled (exit 137) and restarting repeatedly; "
        f"container RSS is climbing toward its {mem}MB memory limit, then the kernel "
        f"OOM-killer terminates it. replicas={replicas}.\n"
        f"SLO breached: {slo}.\n"
        f"Topology: '{fault_node}' is an isolated, stateless service with no downstream "
        f"dependencies (no shared datastore, no callers)."
    )


def _build_cascade_prompt(spec: ScenarioSpec, fault_node: str) -> str:
    """A misleading incident snapshot: the LOUD symptom is on the product victims and a
    recent deploy is the tempting red herring. The smoking gun is NOT spoon-fed — the
    model must infer the root is upstream from the topology (all products fail through the
    same shared api-gateway -> control-plane path). Does NOT name the root cause or the fix."""
    victims = [s.node for s in spec.slo if s.node and s.node != fault_node]
    v0 = victims[0] if victims else "workspace"
    topo = "; ".join(f"{e.src} --{e.type}--> {e.dst}" for e in spec.edges)
    return (
        f"ALERT firing: 503 error-rate spike across MULTIPLE product APIs "
        f"({', '.join(victims) if victims else 'workspace, compute-api, bigquery-api'}) at once.\n"
        f"Observed error_rate_pct (loudest first): {v0} 62%, "
        f"{victims[1] if len(victims) > 1 else 'compute-api'} 57%, api-gateway 40%.\n"
        f"Recent change: a '{v0}' deploy completed ~8 minutes before the spike began "
        f"(rollout reports complete; image bumped a minor version).\n"
        f"Logs (sampled): {v0}: 'request failed: 503 from api-gateway'; "
        f"api-gateway: 'upstream auth/quota check returned 503' (x hundreds).\n"
        f"Topology: {topo}.\n"
        f"(Note: cloud-service-health monitors {fault_node} and the status page is lagging/stale.)\n"
        f"SLO breached: error_rate_pct higher-bad 5 on "
        f"{', '.join(victims) if victims else 'the product APIs'}.\n"
        f"Identify the ROOT cause (it may be UPSTREAM of the loudest alerts — note that ALL "
        f"products are failing simultaneously through a shared path) and remediate it."
    )


def load_scenario(name: str) -> Scenario:
    if name not in _SCENARIOS:
        raise KeyError(f"unknown scenario {name!r} (have {sorted(_SCENARIOS)})")
    cfg = _SCENARIOS[name]
    spec = load_spec(os.path.join(REPO, cfg["path"]))
    rc = spec.root_cause
    fault_node = rc.location.split("->")[0].strip()
    fix_tools = cfg.get("fix_tools") or {a.tool for a in spec.canonical_fix.steps}
    traps = cfg.get("traps") or [{"tool": a.tool, "target": a.args.get("target")}
                                 for a in spec.trap_actions]
    keywords = list(_KIND_KEYWORDS.get(rc.kind, [rc.kind])) + [fault_node]
    prompt = (_build_cascade_prompt if cfg["style"] == "cascade"
              else _build_leaf_prompt)(spec, fault_node)
    return Scenario(
        name=name, spec=spec, fault_node=fault_node, kind=rc.kind,
        category=_KIND_CATEGORY.get(rc.kind, "unknown"),
        correct_fix_tools=set(fix_tools), trap_actions=traps,
        root_cause_keywords=keywords,
        gold_root_description=cfg["gold_root"], red_herring_hints=cfg["red_herrings"],
        prompt_text=prompt,
    )


def is_safe(action: dict, state: dict):
    """Phase-1 STUB — allow everything. Replaced by real rules in Phase 2."""
    return (True, "")


_SUPPORTED_METRICS = {"error_rate_pct", "p99_latency_ms"}


def _resolved(world: World, spec: ScenarioSpec) -> bool:
    if not world.root_cleared:
        return False
    primary = spec.slo[0].node if spec.slo else None
    for s in spec.slo:
        if s.metric not in _SUPPORTED_METRICS:
            continue
        val = world.metric(s.node or primary, s.metric)
        if s.direction == "higher_bad" and val >= s.threshold:
            return False
        if s.direction == "lower_bad" and val <= s.threshold:
            return False
    return True


def run_plan(plan: dict, scenario: Scenario, settle_ticks: int = 5) -> dict:
    world = World.from_spec(scenario.spec, inject=True)
    world.run(ticks=2)
    blocked, applied = [], []
    for a in plan.get("actions", []):
        ok, reason = is_safe(a, {"world": world, "scenario": scenario})
        if not ok:
            blocked.append({"action": a, "reason": reason})
            continue
        apply_action(world, Action(a.get("tool", ""), a.get("args", {})))
        applied.append(a)
    world.run(ticks=settle_ticks)
    return {
        "resolved": _resolved(world, scenario.spec),
        "root_cleared": world.root_cleared,
        "blocked_actions": blocked,
        "applied_actions": applied,
        "final_metrics": dict(world.nodes[scenario.fault_node]),
    }
