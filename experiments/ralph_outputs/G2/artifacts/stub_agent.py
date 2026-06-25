#!/usr/bin/env python3
"""Deterministic SREGym-shaped stub agent (task G2 proof obligation).

This is NOT Stratus. It is a tiny deterministic policy that drives our SREGymEnv through
the SAME tool contract a real SREGym agent uses (reset -> read metrics/logs ->
submit_diagnosis -> cluster_control -> submit_mitigation). Its purpose is to PROVE the
adapter actually runs an external-style agent loop against our scenarios and returns a
REAL engine verdict (not a hardcoded pass). Stratus is a drop-in at this same contract.

It runs two episodes so the verdict is demonstrably falsifiable:
  * SOLVE  — issue the canonical fix on the fault node          -> expect resolved=True
  * TRAP   — issue a non-remediating tool (restart_pod)          -> expect resolved=False
and also exercises the kubectl passthrough + diagnosis grader.

Usage:
    python experiments/ralph_outputs/G2/artifacts/stub_agent.py \
        --scenario scenarios/cidg/22-leaf-bad-deploy-positive.yaml
"""
from __future__ import annotations

import argparse
import json
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from sregym_adapter import SREGymEnv  # noqa: E402

_KIND_WORD = {  # one keyword the stub puts in its NL diagnosis so the grader passes
    "mem_leak": "memory leak", "cpu_starve": "cpu saturation",
    "bad_revision": "bad deploy revision", "bad_content": "bad deploy content",
    "disk_fill": "disk full", "pool_leak": "connection pool leak",
    "fd_exhaust": "file descriptor exhaustion", "thread_exhaust": "thread exhaustion",
    "config_bloat": "config bloat control plane", "cert_expire": "cert expired",
    "cache_flush": "cache flush cold", "node_notready": "node notready",
    "net_delay": "network latency", "dns_race": "dns race",
    "dep_revoked": "dependency revoked quota", "defense_amplify": "defense amplify policy",
    "host_agent_crash": "host agent crash",
}


def _episode(scenario: str, mode: str) -> dict:
    env = SREGymEnv(scenario)
    obs = env.reset()
    fault = env.fault_node

    # --- observe (every read tool family is touched) ---
    metrics = env.get_metrics()
    _logs = env.get_logs()
    _traces = env.get_traces(fault)

    # --- diagnosis phase: NL root cause naming the worst node + kind keyword ---
    worst = max(metrics, key=lambda n: metrics[n]["error_rate_pct"])
    diag_text = f"The root cause is a {_KIND_WORD.get(env.kind, env.kind)} on {fault}."
    diag = env.submit_diagnosis(diag_text)

    # --- mitigation phase ---
    if mode == "solve":
        act = env.cluster_control(tool=env.canonical_fix_tool(), args={"target": fault})
    else:  # trap: deliberately wrong (non-remediating) tool
        act = env.cluster_control(tool="restart_pod", args={"target": fault})
    mit = env.submit_mitigation()

    return {"mode": mode, "scenario": os.path.basename(scenario),
            "worst_node": worst, "diagnosis": diag, "action": act,
            "mitigation": mit, "fidelity": env.fidelity()}


def _kubectl_demo(scenario: str) -> dict:
    """Show the kubectl passthrough + the fidelity (untranslated) counter."""
    env = SREGymEnv(scenario)
    env.reset()
    fault = env.fault_node
    good = env.cluster_control(command=f"kubectl rollout undo deploy/{fault}")
    bad = env.cluster_control(command="kubectl edit configmap app-flags")  # unmappable
    return {"kubectl_good": good, "kubectl_unmappable": bad, "fidelity": env.fidelity()}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenario", default="scenarios/cidg/22-leaf-bad-deploy-positive.yaml")
    a = ap.parse_args()

    solve = _episode(a.scenario, "solve")
    trap = _episode(a.scenario, "trap")
    kube = _kubectl_demo(a.scenario)

    print(json.dumps({"solve": solve, "trap": trap, "kubectl": kube}, indent=2))

    # contract assertions (the whole point: the verdict is REAL + falsifiable)
    ok = (solve["mitigation"]["resolved"] is True
          and trap["mitigation"]["resolved"] is False
          and solve["diagnosis"]["diagnosis_correct"] is True
          and kube["kubectl_unmappable"]["untranslated"] is True)
    print("\nCONTRACT_OK:", ok)
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
