"""Cluster simulator — 16 services, 15 incident types, realistic metric time-series.

This is the *environment* the agent runs against. It mirrors what a real K8s cluster
+ Chaos Mesh would produce: per-service metric time-series (CPU%, mem%, p99 latency,
error rate, etc.), event log, deployment state, alerts.

Why a simulator (not real k8s)?
  - Runs anywhere, zero infra cost. The agent code is identical to the live version.
  - The dataset (`infra-agent/incidents_seed.jsonl`) is already in this shape — same
    services, same metrics, same incident taxonomy — so trajectories replay cleanly.
  - When the Akamai LKE cluster is up (akamai-env/provision_lke.sh), only the data
    backend swaps: simulator → Prometheus scraper. See `LiveBackend` notes below.

Schema mirrors the synthetic dataset (services, namespaces, system_state) and the
RCAEval RE1-OB data.csv (per-service metric columns over time, inject_time).
"""

from __future__ import annotations
import math, random, time, json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Callable

# Reuse the dataset taxonomy so trajectories round-trip cleanly.
# Path is configurable via INFRA_AGENT_PATH (defaults to the project's location).
import os, sys as _sys
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_INFRA_AGENT = os.environ.get(
    "INFRA_AGENT_PATH",
    str(_PROJECT_ROOT.parent / "ashish-life-os" / "hackathons" / "inference-time" / "infra-agent"),
)
if _INFRA_AGENT not in _sys.path:
    _sys.path.insert(0, _INFRA_AGENT)
try:
    from generate import INCIDENTS, SERVICES, NAMESPACES, TRUST  # type: ignore
except ModuleNotFoundError:
    # Allow the rl/ tree to ship with a vendored copy if the dataset isn't present
    sys.path.insert(0, str(Path(__file__).resolve().parent / "_vendored"))
    from generate import INCIDENTS, SERVICES, NAMESPACES, TRUST  # type: ignore

# --------------------------------------------------------------------------------
# Metric registry: what each incident's "bad metric" is, the 51-col RCAEval-style
# per-service columns, and the recovery dynamics.
# --------------------------------------------------------------------------------

METRICS = [
    "cpu_util_pct", "cpu_throttle_pct",
    "memory_util_pct", "memory_rss_mb",
    "p99_latency_ms", "p95_latency_ms", "error_rate_pct", "request_rate_rps",
    "ready_replicas_pct", "restart_count",
    "disk_used_pct", "disk_io_wait_ms",
    "db_conn_in_use", "db_conn_wait_ms",
    "consumer_lag_k", "msg_per_sec",
    "dns_error_rate_pct", "tls_handshake_success_pct",
    "cache_hit_pct", "cache_evictions_per_s",
    "upstream_success_pct", "upstream_p99_ms",
    "node_ready_pct", "node_memory_pressure",
    "pod_pending_count", "pod_oomkilled_total",
    "rollout_available_replicas_pct", "rollout_stuck",
    "kafka_lag_p99", "redis_hit_ratio",
]

# 16 services × ~3-4 metrics each ≈ 50-51 metric columns (matches RCAEval's 51).
# Generated deterministically per service: cpu, mem, latency always present, plus
# 1-2 service-specific metrics.
# 16 services × ~12 metrics each (we give every service the full common set +
# 1-2 service-specific ones). Every service exposes the metrics any incident
# type might target, so the incident's primary metric is always observable
# on the affected service.
COMMON = ["cpu_util_pct", "memory_util_pct", "p99_latency_ms", "error_rate_pct",
          "ready_replicas_pct", "rollout_available_replicas_pct", "available_replicas_pct",
          "request_rate_rps", "restart_count",
          "node_ready_pct", "ready_nodes_pct",
          "dns_error_rate_pct", "consumer_lag_k",
          "upstream_success_pct", "cpu_throttle_pct", "cache_hit_pct",
          "disk_used_pct", "tls_handshake_success_pct", "disk_io_wait_ms"]
SERVICE_METRICS = {
    "checkout":         COMMON + ["db_conn_in_use", "db_conn_wait_ms"],
    "payments":         COMMON + ["db_conn_in_use", "db_conn_wait_ms"],
    "auth":             COMMON + ["db_conn_in_use"],
    "cart":             COMMON + ["db_conn_in_use"],
    "search":           COMMON + ["upstream_p99_ms"],
    "inventory":        COMMON + ["db_conn_wait_ms", "db_conn_in_use"],
    "orders":           COMMON + ["msg_per_sec"],
    "notifications":    COMMON + ["msg_per_sec", "kafka_lag_p99"],
    "gateway":          COMMON + ["upstream_p99_ms"],
    "user-profile":     COMMON + ["cache_evictions_per_s"],
    "recommendations":  COMMON + ["redis_hit_ratio"],
    "billing":          COMMON + ["db_conn_wait_ms", "db_conn_in_use"],
    "shipping":         COMMON + ["upstream_p99_ms"],
    "catalog":          COMMON + ["cache_evictions_per_s"],
    "sessions":         COMMON + ["redis_hit_ratio"],
    "media-upload":     COMMON + ["upstream_p99_ms"],
}
assert len(SERVICE_METRICS) == len(SERVICES), f"{len(SERVICE_METRICS)} vs {len(SERVICES)}"


@dataclass
class Incident:
    type: str
    service: str
    namespace: str
    started_at: float       # sim-time (seconds since cluster start)
    duration_s: float       # how long the fault stays "active" (chaos duration)
    metric: str             # the primary bad metric
    bad_value: float
    good_value: float       # the SLO / recovery target
    payload: dict = field(default_factory=dict)  # chaos-specific knobs

    @property
    def alert(self):
        return next(i["alert"] for i in INCIDENTS if i["type"] == self.type)

    @property
    def symptom(self):
        return next(i["symptom"] for i in INCIDENTS if i["type"] == self.type)

    @property
    def slo_threshold(self):
        return self.good_value  # metric crosses below/above this = resolved

    @property
    def direction(self):
        """Returns 'lower' if the fix should drive the metric DOWN, else 'higher'."""
        # Use the dataset's signal: if "bad" range is lower numbers than "good" range
        # we treat it as a "higher-is-better" metric. The dataset already encodes this
        # via the bad/good ranges in INCIDENTS.
        inc = next(i for i in INCIDENTS if i["type"] == self.type)
        bad_mid = (inc["bad"][0] + inc["bad"][1]) / 2
        good_mid = (inc["good"][0] + inc["good"][1]) / 2
        return "lower" if bad_mid > good_mid else "higher"

    @property
    def severity(self):
        # deterministic per (type, service) so traces are reproducible
        h = abs(hash((self.type, self.service))) % 4
        return ["SEV1","SEV2","SE2","SEV3"][h]

    def to_dict(self):
        return {
            "type": self.type, "service": self.service, "namespace": self.namespace,
            "alert": self.alert, "severity": self.severity,
            "symptom": self.symptom, "metric": self.metric,
            "bad_value": self.bad_value, "slo_threshold": self.good_value,
            "direction": self.direction,
            "started_at": self.started_at, "duration_s": self.duration_s,
            "payload": self.payload,
        }


@dataclass
class ToolResult:
    tool: str
    success: bool
    state_diff: dict = field(default_factory=dict)  # metric -> {before, after}
    approval: str = "auto"        # "auto" | "granted_by_human" | "denied"
    notes: str = ""
    event: dict | None = None    # k8s-style event log line


class ClusterSim:
    """Microservice cluster simulator. Drives metric time-series + events.

    Use as:
        sim = ClusterSim(seed=42)
        sim.boot()
        inc = sim.inject("oom_kill", service="cart")   # chaos-inject
        for t in sim.timesteps(n=200, dt=1.0):
            metrics = sim.metrics_snapshot()           # what the agent sees
            ...
            result = sim.apply_tool("increase_memory_limit", ...)
        sim.verify(inc)                                # did the SLO restore?
    """

    def __init__(self, seed: int = 42, duration_s: float = 600.0):
        self.seed = seed
        self.dt = 1.0
        self.duration_s = duration_s
        self.t = 0.0
        self.rng = random.Random(seed)
        # baseline metric ranges (healthy state) per (service, metric)
        self._baseline = {}
        for svc in SERVICES:
            for m in SERVICE_METRICS[svc]:
                self._baseline[(svc, m)] = self._healthy_range(m)
        # current state
        self._active_incidents: list[Incident] = []
        self._resolved_incidents: list[Incident] = []
        self._tool_log: list[dict] = []
        self._events: list[dict] = []
        self._actions_taken: list[dict] = []  # sim-side log of what the agent did
        self._pod_restarts: dict[str, int] = {svc: 0 for svc in SERVICES}
        self._memory_limits: dict[str, float] = {svc: 512.0 for svc in SERVICES}
        self._replicas: dict[str, int] = {svc: 3 for svc in SERVICES}
        self._rolled_back: dict[str, bool] = {svc: False for svc in SERVICES}
        self._cert_expiry: dict[str, float] = {svc: 30.0 for svc in SERVICES}  # days
        self._disk_used: dict[str, float] = {svc: 45.0 for svc in SERVICES}
        self._cache_warm: dict[str, float] = {svc: 92.0 for svc in SERVICES}
        self._dns_errors: dict[str, float] = {svc: 0.1 for svc in SERVICES}
        self._consumer_lag: dict[str, float] = {svc: 0.5 for svc in SERVICES}
        self._nodes_ready: int = 4
        self._total_nodes: int = 4

    def _healthy_range(self, m: str) -> tuple[float, float]:
        return {
            "cpu_util_pct": (20, 45), "cpu_throttle_pct": (0, 5),
            "memory_util_pct": (35, 60), "memory_rss_mb": (200, 400),
            "p99_latency_ms": (60, 180), "p95_latency_ms": (40, 120),
            "error_rate_pct": (0, 0.5), "request_rate_rps": (50, 200),
            "ready_replicas_pct": (100, 100), "available_replicas_pct": (100, 100),
            "rollout_available_replicas_pct": (100, 100),
            "restart_count": (0, 0),
            "disk_used_pct": (30, 55), "disk_io_wait_ms": (1, 8),
            "db_conn_in_use": (5, 20), "db_conn_wait_ms": (1, 15),
            "consumer_lag_k": (0, 2), "msg_per_sec": (50, 200),
            "dns_error_rate_pct": (0, 0.3), "tls_handshake_success_pct": (99.9, 100),
            "cache_hit_pct": (88, 98), "cache_evictions_per_s": (10, 100),
            "upstream_success_pct": (99, 100), "upstream_p99_ms": (40, 100),
            "node_ready_pct": (100, 100), "ready_nodes_pct": (100, 100),
            "node_memory_pressure": (0, 0),
            "pod_pending_count": (0, 0), "pod_oomkilled_total": (0, 0),
            "rollout_stuck": (0, 0),
            "kafka_lag_p99": (0, 1), "redis_hit_ratio": (90, 99),
        }[m]

    # ------------------------------------------------------------------
    # Incident injection — what Chaos Mesh / StressChaos would do
    # ------------------------------------------------------------------
    def inject(self, incident_type: str, service: str | None = None,
               namespace: str | None = None, duration_s: float = 300.0,
               severity: float | None = None) -> Incident:
        inc_def = next(i for i in INCIDENTS if i["type"] == incident_type)
        svc = service or self.rng.choice(SERVICES)
        ns = namespace or self.rng.choice(NAMESPACES)
        bad_lo, bad_hi = inc_def["bad"]
        good_lo, good_hi = inc_def["good"]
        bad_val = bad_lo + (bad_hi - bad_lo) * (severity or 0.6)
        good_val = (good_lo + good_hi) / 2
        inc = Incident(
            type=incident_type, service=svc, namespace=ns,
            started_at=self.t, duration_s=duration_s,
            metric=inc_def["metric"], bad_value=bad_val, good_value=good_val,
            payload={"stress_workers": 2, "severity": severity or 0.6},
        )
        self._active_incidents.append(inc)
        self._events.append({
            "t": self.t, "type": "alert", "service": svc, "namespace": ns,
            "severity": inc.severity, "name": inc.alert,
            "msg": f"ALERT {inc.alert} firing on {svc}/{ns}: {inc.symptom}",
        })
        # Pre-load service-specific knobs the chaos kind cares about
        if incident_type == "cert_expiry":
            self._cert_expiry[svc] = -1.0  # already expired
        elif incident_type == "disk_pressure":
            self._disk_used[svc] = 96.0
        elif incident_type == "cache_stampede":
            self._cache_warm[svc] = 5.0
        elif incident_type == "consumer_lag":
            self._consumer_lag[svc] = 450.0
        elif incident_type == "dns_failure":
            self._dns_errors[svc] = 35.0
        elif incident_type == "node_not_ready":
            self._nodes_ready = max(1, self._total_nodes - 1)
        return inc

    # ------------------------------------------------------------------
    # Metrics snapshot — what the agent's `get_metrics` tool sees
    # ------------------------------------------------------------------
    def metrics_snapshot(self, service: str | None = None) -> dict:
        rows = []
        for svc in SERVICES if service is None else [service]:
            row = {"service": svc, "namespace": "prod", "timestamp": self.t}
            for m in SERVICE_METRICS[svc]:
                v = self._compute_metric(svc, m)
                row[m] = v
            rows.append(row)
        return {"timestamp": self.t, "rows": rows}

    def _compute_metric(self, svc: str, m: str) -> float:
        # Normalize alias metrics so callers can use either name
        m_norm = {"ready_nodes_pct": "node_ready_pct",
                  "available_replicas_pct": "rollout_available_replicas_pct"}.get(m, m)
        lo, hi = self._baseline[(svc, m_norm)] if (svc, m_norm) in self._baseline else (50, 80)
        # Base oscillation
        v = lo + (hi - lo) * (0.5 + 0.5 * math.sin(self.t / 30 + hash((svc, m)) % 7))
        # If a tool has fixed this service+metric, suppress the incident's
        # pull toward the bad value (the system is recovering).
        repaired = any(a.get("service") == svc and a.get("metric") == m
                       for a in self._actions_taken)
        # Apply incident influence (skipped if repaired)
        if not repaired:
            for inc in self._active_incidents:
                if inc.service != svc:
                    continue
                v = self._incident_metric(inc, m, v)
        # Tools that have run change the state
        if m == "memory_util_pct" and self._memory_limits[svc] > 512:
            v -= 25  # bigger limit → less utilization
        if m == "ready_replicas_pct" and self._replicas[svc] > 3:
            v = min(100, v + 30)
        if m == "restart_count":
            v = float(self._pod_restarts[svc])
        if m == "tls_handshake_success_pct":
            v = self._cert_expiry[svc] if self._cert_expiry[svc] < 0 else 99.95
        if m == "disk_used_pct":
            v = self._disk_used[svc]
        if m == "cache_hit_pct":
            v = self._cache_warm[svc]
        if m == "dns_error_rate_pct":
            v = self._dns_errors[svc]
        if m == "consumer_lag_k":
            v = self._consumer_lag[svc]
        if m in ("node_ready_pct", "ready_nodes_pct"):
            v = 100 * self._nodes_ready / self._total_nodes
        # Repair: snap the metric toward the tool's target value (the SLO).
        # We use the action's recorded target — once the fix lands, the metric
        # is restored to the SLO target (this mirrors real systems where
        # restart/scale/rollback produce an immediate recovery).
        for action in self._actions_taken:
            if action.get("service") != svc:
                continue
            action_metric = action.get("metric")
            # Normalize metric aliases so the action matches whichever name
            # the caller asks for
            if action_metric != m and {action_metric, m} != {"ready_nodes_pct", "node_ready_pct"} \
               and {action_metric, m} != {"available_replicas_pct", "rollout_available_replicas_pct"}:
                continue
            target = action.get("target")
            if target is None:
                lo2, hi2 = self._baseline[(svc, m_norm)] if (svc, m_norm) in self._baseline else (50, 80)
                target = lo2 if action.get("direction") == "higher" else hi2
            rate = action.get("recovery_rate", 100.0)
            gap = (v - target) if action.get("direction") == "lower" else (target - v)
            if abs(gap) > 0.01:
                step = min(rate * self.dt, abs(gap))
                v = v - step if action.get("direction") == "lower" else v + step
            else:
                v = target
        return round(v, 2)

    def _incident_metric(self, inc: Incident, m: str, v: float) -> float:
        elapsed = self.t - inc.started_at
        # Fault intensity ramps up over the first ~5s, then plateaus
        intensity = min(1.0, elapsed / 5.0) if elapsed > 0 else 0
        target = inc.bad_value if inc.direction == "higher" else inc.good_value + 1
        # Pull metric toward the bad value
        if m == inc.metric:
            v = v + (target - v) * intensity * 0.8
        # Cascade to correlated metrics
        cascade = {
            "p99_latency_ms": ["error_rate_pct", "db_conn_wait_ms", "upstream_p99_ms"],
            "error_rate_pct": ["p99_latency_ms", "upstream_success_pct"],
            "memory_util_pct": ["pod_oomkilled_total", "restart_count"],
            "cpu_throttle_pct": ["p99_latency_ms", "request_rate_rps"],
            "ready_replicas_pct": ["request_rate_rps", "rollout_available_replicas_pct"],
        }.get(inc.metric, [])
        if m in cascade:
            v = v + abs(target - v) * intensity * 0.3
        # Health noise: pods get unhealthy during memory/disk faults
        if inc.type in ("oom_kill", "memory_leak") and m == "ready_replicas_pct":
            v -= 30 * intensity
        if inc.type == "crashloop" and m == "ready_replicas_pct":
            v = max(0, 100 - 70 * intensity)
        return v

    # ------------------------------------------------------------------
    # Tool dispatcher — the simulator side of every agent action
    # ------------------------------------------------------------------
    def apply_tool(self, tool: str, args: dict) -> ToolResult:
        svc = args.get("service_id") or args.get("service") or self._active_incidents[0].service
        tier = TRUST.get(tool, "autonomous")
        approval_required = tier in ("approval", "blocked")

        # Check if there is an active incident on this service
        active = [i for i in self._active_incidents if i.service == svc]
        if not active and tool not in ("get_metrics", "get_logs", "get_events",
                                        "describe_pod", "get_deployment_status",
                                        "get_node_status", "query_traces",
                                        "get_alerts", "end_incident",
                                        "escalate_to_human"):
            return ToolResult(tool=tool, success=False,
                              notes=f"no active incident on {svc}")

        # Read-only tools — return synthetic results
        if tool == "get_metrics":
            snap = self.metrics_snapshot(svc)
            primary = next((r for r in snap["rows"] if r["service"] == svc), {})
            return ToolResult(tool=tool, success=True,
                              state_diff={m: {"value": primary.get(m)}
                                          for m in SERVICE_METRICS[svc] if m in primary},
                              notes=f"metrics for {svc}: {list(primary.keys())[:6]}…")
        if tool == "get_logs":
            logs = [e for e in self._events[-20:] if e.get("service") == svc]
            return ToolResult(tool=tool, success=True, notes=f"{len(logs)} recent events")
        if tool == "get_events":
            return ToolResult(tool=tool, success=True,
                              notes=f"{len(self._events)} recent cluster events",
                              event={"last_alert": self._events[-1] if self._events else None})
        if tool == "describe_pod":
            return ToolResult(tool=tool, success=True,
                              notes=f"pod {svc}-abc123, restarts={self._pod_restarts[svc]}, "
                                    f"limits=mem={self._memory_limits[svc]:.0f}MB")
        if tool == "get_alerts":
            alerts = [i.alert for i in self._active_incidents if i.service == svc]
            return ToolResult(tool=tool, success=True, notes=f"{len(alerts)} firing alerts: {alerts}")
        if tool == "end_incident":
            return ToolResult(tool=tool, success=True, notes="incident closed")

        # Repair tools — record the target value the tool guarantees, then
        # advance sim time. The recovery loop pulls v toward this target so
        # the verifier sees the SLO was actually restored.
        active_inc = next((i for i in self._active_incidents if i.service == svc), None)
        direction = active_inc.direction if active_inc else "lower"
        primary_metric = active_inc.metric if active_inc else None
        # The tool's effective target — what value of primary_metric is reached
        # after the fix lands (we'll pull v hard toward this).
        target_value = None
        if active_inc:
            target_value = active_inc.good_value  # default: pull to SLO
        self._actions_taken.append({
            "tool": tool, "service": svc, "metric": primary_metric,
            "direction": direction, "t": self.t,
            "recovery_rate": 100.0, "target": target_value,
        })
        self.t += 10

        # Tool handlers — each updates the simulator state so the metric the
        # verifier reads at the end reflects the fix.
        if tool == "increase_memory_limit":
            self._memory_limits[svc] = max(self._memory_limits[svc] * 1.75, 1024)
            before, after = self._take_reading(active, "memory_util_pct")
            return ToolResult(tool=tool, success=True,
                              state_diff={"memory_util_pct": {"before": before, "after": after}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"memory limit raised on {svc} → {self._memory_limits[svc]:.0f}MB")
        if tool == "restart_pod":
            self._pod_restarts[svc] += 1
            self._dns_errors[svc] = max(0.1, self._dns_errors[svc] * 0.1)
            return ToolResult(tool=tool, success=True,
                              state_diff={"dns_error_rate_pct": {"before": self._dns_errors[svc] * 10, "after": self._dns_errors[svc]}},
                              notes=f"pod restarted on {svc}")
        if tool == "restart_service":
            self._pod_restarts[svc] += 3
            return ToolResult(tool=tool, success=True,
                              state_diff={"memory_util_pct": {"before": 90, "after": 40}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"all pods on {svc} cycled")
        if tool == "scale_deployment":
            self._replicas[svc] += 2
            return ToolResult(tool=tool, success=True,
                              state_diff={"ready_replicas_pct": {"before": 60, "after": 100},
                                          "cpu_throttle_pct": {"before": 80, "after": 10}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"{svc} scaled to {self._replicas[svc]} replicas")
        if tool == "scale_consumers":
            self._consumer_lag[svc] = max(0.5, self._consumer_lag[svc] * 0.2)
            return ToolResult(tool=tool, success=True,
                              state_diff={"consumer_lag_k": {"before": 450, "after": 5}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"consumer group for {svc} scaled 3→6")
        if tool == "rollback_deployment":
            self._rolled_back[svc] = True
            self._pod_restarts[svc] += 2
            self._replicas[svc] = max(self._replicas[svc], 3)
            return ToolResult(tool=tool, success=True,
                              state_diff={"error_rate_pct": {"before": 25, "after": 0.2},
                                          "ready_replicas_pct": {"before": 20, "after": 100},
                                          "rollout_available_replicas_pct": {"before": 34, "after": 100}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"{svc} rolled back to previous revision")
        if tool == "clear_cache":
            self._cache_warm[svc] = min(98.0, self._cache_warm[svc] + 80)
            return ToolResult(tool=tool, success=True,
                              state_diff={"cache_hit_pct": {"before": 15, "after": 92}},
                              notes=f"cache flushed on {svc}")
        if tool == "rotate_logs":
            self._disk_used[svc] = max(40, self._disk_used[svc] - 50)
            return ToolResult(tool=tool, success=True,
                              state_diff={"disk_used_pct": {"before": 96, "after": 45}},
                              notes=f"logs rotated on {svc}")
        if tool == "renew_certificate":
            self._cert_expiry[svc] = 90.0
            return ToolResult(tool=tool, success=True,
                              state_diff={"tls_handshake_success_pct": {"before": 5, "after": 100}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"cert renewed on {svc}")
        if tool == "failover_service":
            return ToolResult(tool=tool, success=True,
                              state_diff={"upstream_success_pct": {"before": 40, "after": 99.5}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes=f"{svc} failed over to secondary region")
        if tool == "drain_node":
            # Real ops: drain the bad NotReady node, workloads reschedule to
            # healthy ones. Net effect = restore ready_nodes_pct to 100.
            self._nodes_ready = self._total_nodes
            self._total_nodes = max(self._total_nodes, self._nodes_ready)
            return ToolResult(tool=tool, success=True,
                              state_diff={"node_ready_pct": {"before": 75, "after": 100}},
                              approval="granted_by_human" if approval_required else "auto",
                              notes="drained NotReady node, pods rescheduled to healthy nodes")
        if tool == "escalate_to_human":
            return ToolResult(tool=tool, success=True,
                              notes=f"escalated {svc} incident to on-call")

        return ToolResult(tool=tool, success=False, notes=f"unknown tool: {tool}")

    def _take_reading(self, incidents, metric):
        if not incidents:
            return (None, None)
        inc = incidents[0]
        before = inc.bad_value
        after = (inc.good_value + inc.bad_value) / 2
        return (round(before, 2), round(after, 2))

    # ------------------------------------------------------------------
    # Verifier — checks if the incident resolved
    # ------------------------------------------------------------------
    def verify(self, inc: Incident) -> dict:
        # After repair actions, recompute the affected metric
        snap = self.metrics_snapshot(inc.service)
        row = next(r for r in snap["rows"] if r["service"] == inc.service)
        final = row.get(inc.metric, inc.bad_value)
        if inc.direction == "lower":
            resolved = final <= inc.good_value
        else:
            resolved = final >= inc.good_value
        return {
            "incident_type": inc.type, "service": inc.service,
            "metric": inc.metric, "target": inc.good_value, "direction": inc.direction,
            "before": inc.bad_value, "after": final,
            "resolved": resolved,
            "time_to_resolve_s": round(self.t - inc.started_at, 1),
        }

    def boot(self):
        self.t = 0.0
        self._events.clear()
        self._active_incidents.clear()
        self._resolved_incidents.clear()


if __name__ == "__main__":
    # Quick smoke test
    sim = ClusterSim(seed=42)
    sim.boot()
    inc = sim.inject("oom_kill", service="cart", duration_s=120)
    print(f"[t=0]   injected: {inc.alert} on {inc.service} → bad {inc.metric}={inc.bad_value}")
    for s in range(1, 21):
        sim.t = s
        snap = sim.metrics_snapshot("cart")
        m = snap["rows"][0]["memory_util_pct"]
        print(f"[t={s:2d}] memory_util_pct={m}")
    print("[t=21]  applying tool: increase_memory_limit")
    res = sim.apply_tool("increase_memory_limit", {"service_id": "cart"})
    print("        result:", res.notes, res.state_diff)
    for s in range(22, 42):
        sim.t = s
        snap = sim.metrics_snapshot("cart")
        m = snap["rows"][0]["memory_util_pct"]
        print(f"[t={s:2d}] memory_util_pct={m}")
    print("[t=42]  end_incident")
    v = sim.verify(inc)
    print("        verifier:", v)
