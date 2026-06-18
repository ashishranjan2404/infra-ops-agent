#!/usr/bin/env python3
"""
Synthesize platform-engineering / SRE incident-resolution trajectories in the
SAME schema as Beibei's FIREBALL Path-A data (so the training pipeline needs no
changes).

FIREBALL analogy:
  state_before (HP/pos/slots)  -> system_state (metrics/logs/alerts)
  action (cast/attack/heal)    -> tool (restart/scale/rollback/...)
  state_after (damage/kills)   -> incident resolved or not

Usage:
  python generate.py --n 2000                 # seed set
  python generate.py --n 150000 --out incidents.jsonl
"""
from __future__ import annotations
import argparse, json, random, statistics as st
from collections import Counter

# ---------------------------------------------------------------------------
# Tool registry (analogous to fireball tools_registry.json) + trust tiers
# trust_tier feeds the guardrails/RLHF model: autonomous | approval | blocked
# ---------------------------------------------------------------------------
TOOLS = [
    # diagnostics (read-only -> autonomous)
    ("get_metrics", "autonomous", "Fetch current metrics (cpu/mem/latency/error_rate) for a service."),
    ("get_logs", "autonomous", "Tail recent logs for a service/pod."),
    ("get_events", "autonomous", "List recent k8s events for a namespace/pod."),
    ("describe_pod", "autonomous", "Describe a pod: status, restarts, last state, conditions."),
    ("get_deployment_status", "autonomous", "Get rollout status + replica health of a deployment."),
    ("get_node_status", "autonomous", "Get node conditions (Ready, MemoryPressure, DiskPressure)."),
    ("query_traces", "autonomous", "Query distributed traces for slow/error spans."),
    ("get_alerts", "autonomous", "List firing alerts for a service."),
    # low-risk remediation -> autonomous
    ("restart_pod", "autonomous", "Restart (delete) a pod so it is recreated."),
    ("clear_cache", "autonomous", "Flush an application/CDN cache."),
    ("rotate_logs", "autonomous", "Rotate/truncate logs to free disk."),
    # medium-risk remediation -> human approval
    ("scale_deployment", "approval", "Change replica count of a deployment."),
    ("rollback_deployment", "approval", "Roll a deployment back to the previous revision."),
    ("restart_service", "approval", "Restart a service / all its pods."),
    ("increase_memory_limit", "approval", "Raise the container memory limit/request."),
    ("failover_service", "approval", "Fail traffic over to a healthy replica/region."),
    ("renew_certificate", "approval", "Renew/rotate an expiring TLS certificate."),
    ("scale_consumers", "approval", "Scale a queue consumer group to drain backlog."),
    # high-risk -> approval/blocked
    ("drain_node", "blocked", "Cordon + drain a node (evicts workloads)."),
    ("cordon_node", "approval", "Mark a node unschedulable."),
    ("rotate_secret", "blocked", "Rotate a secret/credential."),
    ("modify_network_policy", "blocked", "Change a network policy / firewall rule."),
    ("delete_pvc", "blocked", "Delete a persistent volume claim (data loss risk)."),
    # control (analogous to end_turn / abstain)
    ("end_incident", "autonomous", "Declare the incident resolved and close it out."),
    ("escalate_to_human", "autonomous", "Hand off to an on-call human with context."),
]
TRUST = {name: tier for name, tier, _ in TOOLS}

SYSTEM_PROMPT = (
    "You are a platform-engineering (SRE) agent on call. An incident is firing. "
    "Assess the system state by reading metrics/logs/events, then decide and execute "
    "remediation using the available tools. Respect tool guardrails (some actions need "
    "human approval). End with end_incident once the SLO is restored."
)

SERVICES = ["checkout", "payments", "auth", "cart", "search", "inventory", "orders",
            "notifications", "gateway", "user-profile", "recommendations", "billing",
            "shipping", "catalog", "sessions", "media-upload"]
NAMESPACES = ["prod", "prod-us-east", "prod-eu", "prod-apac", "platform", "edge"]

# ---------------------------------------------------------------------------
# Incident taxonomy — the "list of issues we replicate".
# Each: signals (the firing alert + bad metric), diagnostics the agent should run,
# the correct fix tool, and the resolution check (metric back to normal).
# These are grounded in well-known production incident classes.
# ---------------------------------------------------------------------------
INCIDENTS = [
    {"type": "oom_kill", "alert": "PodOOMKilled",
     "symptom": "container memory exceeded limit; pod OOMKilled and restarting",
     "diag": ["describe_pod", "get_metrics"], "fix": "increase_memory_limit",
     "metric": "memory_util_pct", "bad": (97, 100), "good": (55, 75),
     "extra": "restarts"},
    {"type": "crashloop", "alert": "CrashLoopBackOff",
     "symptom": "pod crash-looping after a bad config/env change",
     "diag": ["describe_pod", "get_logs"], "fix": "rollback_deployment",
     "metric": "ready_replicas_pct", "bad": (0, 20), "good": (100, 100)},
    {"type": "latency_spike", "alert": "HighP99Latency",
     "symptom": "p99 latency above SLO under a traffic surge",
     "diag": ["get_metrics", "query_traces"], "fix": "scale_deployment",
     "metric": "p99_latency_ms", "bad": (1200, 4000), "good": (90, 240)},
    {"type": "bad_deploy_errors", "alert": "ErrorRateSLOburn",
     "symptom": "5xx error rate spiked right after a deploy",
     "diag": ["get_metrics", "get_logs"], "fix": "rollback_deployment",
     "metric": "error_rate_pct", "bad": (12, 45), "good": (0, 1)},
    {"type": "disk_pressure", "alert": "NodeDiskPressure",
     "symptom": "node disk almost full, evictions imminent",
     "diag": ["get_node_status", "get_events"], "fix": "rotate_logs",
     "metric": "disk_used_pct", "bad": (92, 99), "good": (40, 65)},
    {"type": "cert_expiry", "alert": "TLSCertExpiringSoon",
     "symptom": "TLS handshake failures from an expired certificate",
     "diag": ["get_logs", "get_alerts"], "fix": "renew_certificate",
     "metric": "tls_handshake_success_pct", "bad": (0, 30), "good": (100, 100)},
    {"type": "memory_leak", "alert": "MemoryLeakSuspected",
     "symptom": "memory creeping up over hours, GC not reclaiming",
     "diag": ["get_metrics", "describe_pod"], "fix": "restart_service",
     "metric": "memory_util_pct", "bad": (88, 96), "good": (35, 55)},
    {"type": "db_pool_exhaustion", "alert": "DBConnectionPoolExhausted",
     "symptom": "all DB connections in use, requests timing out",
     "diag": ["get_metrics", "get_logs"], "fix": "scale_deployment",
     "metric": "db_conn_wait_ms", "bad": (800, 5000), "good": (2, 30)},
    {"type": "node_not_ready", "alert": "NodeNotReady",
     "symptom": "a node went NotReady (kubelet/network), pods stuck",
     "diag": ["get_node_status", "get_events"], "fix": "drain_node",
     "metric": "ready_nodes_pct", "bad": (60, 85), "good": (100, 100)},
    {"type": "consumer_lag", "alert": "KafkaConsumerLagHigh",
     "symptom": "consumer group lag growing, backlog not draining",
     "diag": ["get_metrics", "get_logs"], "fix": "scale_consumers",
     "metric": "consumer_lag_k", "bad": (120, 900), "good": (0, 5)},
    {"type": "dns_failure", "alert": "CoreDNSResolutionErrors",
     "symptom": "intermittent DNS resolution failures cluster-wide",
     "diag": ["get_logs", "get_events"], "fix": "restart_pod",
     "metric": "dns_error_rate_pct", "bad": (10, 60), "good": (0, 1)},
    {"type": "upstream_5xx", "alert": "UpstreamDependencyDown",
     "symptom": "a dependency is returning 5xx, cascading failures",
     "diag": ["query_traces", "get_metrics"], "fix": "failover_service",
     "metric": "upstream_success_pct", "bad": (20, 70), "good": (99, 100)},
    {"type": "cpu_saturation", "alert": "CPUThrottlingHigh",
     "symptom": "CPU throttled, requests queueing",
     "diag": ["get_metrics", "describe_pod"], "fix": "scale_deployment",
     "metric": "cpu_throttle_pct", "bad": (60, 95), "good": (2, 18)},
    {"type": "stuck_rollout", "alert": "RolloutStuck",
     "symptom": "deployment stuck — readiness probe never passes",
     "diag": ["get_deployment_status", "describe_pod"], "fix": "rollback_deployment",
     "metric": "available_replicas_pct", "bad": (10, 50), "good": (100, 100)},
    {"type": "cache_stampede", "alert": "CacheHitRatioDrop",
     "symptom": "cache hit ratio collapsed, origin overloaded",
     "diag": ["get_metrics", "get_logs"], "fix": "clear_cache",
     "metric": "cache_hit_pct", "bad": (5, 35), "good": (88, 99)},
]

THOUGHT_ASSESS = [
    "Alert {alert} firing on {svc} in {ns}. {symptom}. Let me check the {metric} before acting.",
    "{svc} is paging: {symptom}. First confirm scope by reading {tool}.",
    "Looks like {symptom} on {svc}. Don't act blind — pull {tool} to confirm.",
    "{alert} on {svc}/{ns}. I should verify {metric} rather than assume the cause.",
]
THOUGHT_SECOND = [
    "{metric} is {bad} — well outside SLO. Let me corroborate with {tool} before remediating.",
    "Confirmed degradation ({metric}={bad}). Checking {tool} to pin the cause.",
    "That matches {symptom}. One more signal from {tool} to be sure.",
]
THOUGHT_FIX = [
    "Root cause matches {type}. The correct remediation is {fix}. {gate}",
    "Given the evidence, {fix} is the right fix for {type}. {gate}",
    "This is a textbook {type}. Applying {fix}. {gate}",
]
THOUGHT_END = [
    "{metric} back to {good} — within SLO. Incident resolved.",
    "Remediation worked: {metric} recovered to {good}. Closing out.",
    "System healthy again ({metric}={good}). Ending the incident.",
]

def rint(lo, hi): return random.randint(int(lo), int(hi))

def difficulty_for(inc, n_affected):
    sev = {"autonomous": 0.2, "approval": 0.5, "blocked": 0.8}[TRUST[inc["fix"]]]
    return round(min(0.95, max(0.08, 0.4 * sev + 0.4 * min(n_affected / 8, 1) + random.uniform(0, 0.2))), 2)

def make_trajectory(i):
    inc = random.choice(INCIDENTS)
    svc = random.choice(SERVICES); ns = random.choice(NAMESPACES)
    n_affected = rint(1, 8)
    bad_val = rint(*inc["bad"]); good_val = rint(*inc["good"])
    fix = inc["fix"]; tier = TRUST[fix]
    gate = {"autonomous": "This tool is autonomous — executing.",
            "approval": "This tool needs human approval — requesting it.",
            "blocked": "This tool is guarded — escalating for approval."}[tier]
    metric = inc["metric"]

    system_state = [
        {"service": svc, "namespace": ns, "alert": inc["alert"], "severity": random.choice(["SEV2","SEV3","SEV2","SEV1"])},
        {"metric": metric, "value": bad_val, "slo_threshold": good_val, "affected_pods": n_affected},
    ]
    user_input = {"service_id": svc, "namespace": ns,
                  "incident_context": inc["symptom"],
                  "system_state": system_state}

    steps = []; sn = 0
    # diagnostic 1
    d1 = inc["diag"][0]
    sn += 1; steps.append({"step": sn, "role": "assistant",
        "thought": random.choice(THOUGHT_ASSESS).format(alert=inc["alert"], svc=svc, ns=ns, symptom=inc["symptom"], metric=metric, tool=d1),
        "action": {"tool": d1, "args": {"service_id": svc, "namespace": ns}},
        "label": {"action_correct": True, "thought_quality": round(random.uniform(0.6, 0.85), 2)}})
    sn += 1; steps.append({"step": sn, "role": "tool", "name": d1,
        "content": {"metric": metric, "value": bad_val, "status": "degraded", "affected_pods": n_affected}})
    # diagnostic 2
    d2 = inc["diag"][1]
    sn += 1; steps.append({"step": sn, "role": "assistant",
        "thought": random.choice(THOUGHT_SECOND).format(metric=metric, bad=bad_val, tool=d2, symptom=inc["symptom"]),
        "action": {"tool": d2, "args": {"service_id": svc, "namespace": ns}},
        "label": {"action_correct": True, "thought_quality": round(random.uniform(0.6, 0.85), 2)}})
    sn += 1; steps.append({"step": sn, "role": "tool", "name": d2,
        "content": {"finding": inc["symptom"], "matched_signature": inc["type"]}})
    # the fix
    sn += 1; steps.append({"step": sn, "role": "assistant",
        "thought": random.choice(THOUGHT_FIX).format(type=inc["type"], fix=fix, gate=gate),
        "action": {"tool": fix, "args": {"service_id": svc, "namespace": ns}, "requires_approval": tier != "autonomous"},
        "label": {"action_correct": True, "thought_quality": round(random.uniform(0.7, 0.95), 2)}})
    sn += 1; steps.append({"step": sn, "role": "tool", "name": fix,
        "content": {"success": True,
                    "state_diff": {metric: {"before": bad_val, "after": good_val}},
                    "approval": ("auto" if tier == "autonomous" else "granted_by_human")}})
    # end
    sn += 1; steps.append({"step": sn, "role": "assistant",
        "thought": random.choice(THOUGHT_END).format(metric=metric, good=good_val),
        "action": {"tool": "end_incident", "args": {"service_id": svc}},
        "label": {"action_correct": True, "thought_quality": round(random.uniform(0.55, 0.7), 2)}})

    usefulness = []
    for s in steps:
        if s["role"] != "assistant": continue
        t = s["action"]["tool"]
        usefulness.append(0.3 if t == "end_incident" else (1.4 if t in inc["diag"] else 2.0))
    # interleave None for tool steps to mirror fireball
    gains = []
    ai = 0
    for s in steps:
        if s["role"] == "assistant": gains.append(usefulness[ai]); ai += 1
        else: gains.append(None)

    tools_used = [s["action"]["tool"] for s in steps if s["role"] == "assistant"]
    return {
        "trajectory_id": f"incident_t_{i:06d}",
        "path": "A",
        "seed_input_id": f"{inc['type']}_{svc}_{ns}_{i}",
        "task_type": inc["type"],
        "difficulty": difficulty_for(inc, n_affected),
        "language": "en",
        "system_prompt": SYSTEM_PROMPT,
        "user_input": user_input,
        "trajectory": steps,
        "meta": {
            "construction_path": "synthetic_templated",
            "usefulness_gain_per_step": gains,
            "alternative_paths_count": 1,
            "outcome_correct": True,
            "outcome_match_to_seed": "exact",
            "incident_type": inc["type"],
            "alert": inc["alert"],
            "tools_used": tools_used,
            "fix_tool": fix,
            "fix_trust_tier": tier,
            "required_approval": tier != "autonomous",
        },
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=2000)
    ap.add_argument("--out", default="incidents.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    args = ap.parse_args()
    random.seed(args.seed)

    tt, tiers, tools = Counter(), Counter(), Counter()
    diffs, lengths = [], []
    with open(args.out, "w") as f:
        for i in range(args.n):
            t = make_trajectory(i)
            f.write(json.dumps(t) + "\n")
            tt[t["task_type"]] += 1
            tiers[t["meta"]["fix_trust_tier"]] += 1
            for s in t["trajectory"]:
                if s["role"] == "assistant": tools[s["action"]["tool"]] += 1
            diffs.append(t["difficulty"]); lengths.append(len(t["trajectory"]))

    stats = {
        "total_trajectories": args.n,
        "output_file": args.out,
        "incident_types": dict(tt.most_common()),
        "fix_trust_tier": dict(tiers),
        "tool_frequency": dict(tools.most_common()),
        "difficulty_mean": round(st.mean(diffs), 3),
        "difficulty_min": min(diffs), "difficulty_max": max(diffs),
        "steps_mean": round(st.mean(lengths), 2),
        "n_tools_in_registry": len(TOOLS),
    }
    with open(args.out.replace(".jsonl", "_stats.json"), "w") as f:
        json.dump(stats, f, indent=2)
    # also emit the tool registry as an artifact
    with open("tools_registry.json", "w") as f:
        json.dump([{"name": n, "trust_tier": t, "description": d} for n, t, d in TOOLS], f, indent=2)
    print(json.dumps(stats, indent=2))

if __name__ == "__main__":
    main()
