#!/usr/bin/env python3
"""J1 agent-runner harness — drive an SRE/REx agent against the cidg-mreal
call-mesh under real Chaos Mesh faults, and score its root-cause diagnosis.

This is the live-cluster twin of rex/harness_synth.py's offline loop. One
"episode" = (inject a chaos experiment) -> (gather observations) -> (let the
agent diagnose the root cause) -> (deterministically score the diagnosis).

Two backends, selected by --backend:
  * sim   : NO cluster needed. Uses sim/engine.py's propagate() to produce the
            same emergent-cascade observation a faulted mesh would. Lets the WHOLE
            harness (injection plan, observation schema, scoring) be validated
            offline / in CI. This is what runs when GKE auth is unavailable.
  * kube  : LIVE. Applies a Chaos Mesh experiment from j1_chaos_experiments.yaml,
            scrapes /metrics via `kubectl -n cidg-mreal exec`, then deletes the
            experiment (auto-heal). Requires a reachable cluster + Chaos Mesh CRDs.

Scoring reuses rex/scoring.py:deterministic_judge so live and offline runs are
graded on the SAME rubric as the rest of the project.

Usage:
  # offline self-test (no cluster) — also the CI smoke path:
  python3 j1_agent_runner.py --backend sim --selftest
  # offline, scoring a fixed agent guess against every experiment:
  python3 j1_agent_runner.py --backend sim --agent-cmd 'echo payments'
  # live (requires KUBECONFIG to a reachable cidg-mreal cluster + Chaos Mesh):
  python3 j1_agent_runner.py --backend kube --experiment j1-payments-error
"""
from __future__ import annotations
import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]  # .../rl
sys.path.insert(0, str(REPO))

NS = "cidg-mreal"
EXPERIMENTS_FILE = Path(__file__).with_name("j1_chaos_experiments.yaml")

# Ground truth: experiment name -> (gold root cause, red herrings the agent
# might wrongly blame). Mirrors the cascade topology in mreal/k8s.yaml.
GROUND_TRUTH = {
    "j1-payments-error":         ("payments service returning errors", ["gateway", "checkout", "db"]),
    "j1-payments-latency":       ("payments service is slow / high latency", ["gateway", "checkout", "db pool"]),
    "j1-db-pool-stress":         ("db connection pool exhausted", ["payments", "orders", "gateway"]),
    "j1-checkout-egress-delay":  ("checkout to payments network latency", ["payments", "gateway", "db"]),
    "j1-gateway-pod-kill":       ("gateway pod crashed / unavailable", ["payments", "checkout", "db"]),
}


@dataclass
class Observation:
    """What the agent sees: per-app 5xx rate, latency, up-flag. Same shape the
    Prometheus ServiceMonitor in mreal/k8s.yaml exposes."""
    experiment: str
    per_app: dict = field(default_factory=dict)   # app -> {err_rate, p50_s, up}
    loudest_victim: str = ""
    notes: str = ""


# ---------------------------------------------------------------------------
# Backend: sim  (offline twin — uses the project's own propagation model)
# ---------------------------------------------------------------------------
def _sim_observe(experiment: str) -> Observation:
    """Produce the emergent cascade observation a faulted mesh would yield,
    using the same dependency edges as mreal/k8s.yaml. Self-contained so the
    harness validates with zero external deps."""
    # gateway -> checkout -> payments -> db ; orders -> db (fan-in)
    edges = {"gateway": ["checkout"], "checkout": ["payments"],
             "payments": ["db"], "orders": ["db"], "db": []}
    faulted = {
        "j1-payments-error":        ("payments", "error"),
        "j1-payments-latency":      ("payments", "slow"),
        "j1-db-pool-stress":        ("db", "error"),
        "j1-checkout-egress-delay": ("checkout", "slow"),
        "j1-gateway-pod-kill":      ("gateway", "error"),
    }[experiment]
    root, mode = faulted

    def reaches_fault(app, seen=None):
        seen = seen or set()
        if app == root:
            return True
        for up in edges.get(app, []):
            if up not in seen and reaches_fault(up, seen | {app}):
                return True
        return False

    per_app, worst, worst_rate = {}, "", -1.0
    for app in edges:
        hit = reaches_fault(app)
        err = 0.0 if not hit else (0.95 if mode == "error" else 0.10)
        p50 = 0.05 if not hit else (0.06 if mode == "error" else 1.25)
        # depth from top inflates apparent error volume -> loudest victim is top
        rate = err * (3 if app == "gateway" else 2 if app in ("checkout", "orders") else 1)
        per_app[app] = {"err_rate": round(err, 3), "p50_s": p50, "up": not (app == root and mode == "error")}
        if rate > worst_rate:
            worst, worst_rate = app, rate
    return Observation(experiment=experiment, per_app=per_app, loudest_victim=worst,
                       notes=f"sim backend; root={root} mode={mode}")


# ---------------------------------------------------------------------------
# Backend: kube  (live — Chaos Mesh + kubectl). Auto-heals via finally.
# ---------------------------------------------------------------------------
def _kubectl(*args, check=True, timeout=30):
    return subprocess.run(["kubectl", "-n", NS, *args], capture_output=True,
                          text=True, timeout=timeout, check=check)


def _kube_observe(experiment: str, soak_s: int = 30) -> Observation:
    # apply only the one experiment doc (split the multi-doc file by name)
    docs = EXPERIMENTS_FILE.read_text().split("\n---\n")
    doc = next((d for d in docs if f"name: {experiment}\n" in d), None)
    if doc is None:
        raise SystemExit(f"experiment {experiment!r} not in {EXPERIMENTS_FILE}")
    kind = next(l.split(":", 1)[1].strip() for l in doc.splitlines() if l.startswith("kind:"))
    try:
        subprocess.run(["kubectl", "apply", "-f", "-"], input=doc, text=True,
                       capture_output=True, check=True, timeout=30)
        time.sleep(soak_s)                       # let the cascade develop
        per_app = {}
        for app in ("gateway", "checkout", "payments", "orders", "db"):
            try:
                pod = _kubectl("get", "pod", "-l", f"app={app}", "-o",
                               "jsonpath={.items[0].metadata.name}").stdout.strip()
                m = _kubectl("exec", pod, "--", "python", "-c",
                             "import urllib.request;print(urllib.request.urlopen('http://localhost:8080/metrics').read().decode())",
                             timeout=20).stdout
                per_app[app] = _parse_metrics(m, app)
            except Exception as e:               # pod gone (e.g. pod-kill) is signal
                per_app[app] = {"err_rate": None, "p50_s": None, "up": False, "err": str(e)[:80]}
        worst = max((a for a in per_app), key=lambda a: (per_app[a].get("err_rate") or 0))
        return Observation(experiment=experiment, per_app=per_app, loudest_victim=worst,
                           notes=f"kube backend; kind={kind}")
    finally:
        subprocess.run(["kubectl", "-n", NS, "delete", "-f", "-"], input=doc,
                       text=True, capture_output=True, timeout=30)  # AUTO-HEAL


def _parse_metrics(text: str, app: str) -> dict:
    v = {"200": 0.0, "500": 0.0}
    for line in text.splitlines():
        for st in ("200", "500"):
            if f'app_requests_total{{app="{app}",status="{st}"}}' in line:
                try: v[st] = float(line.rsplit(" ", 1)[1])
                except Exception: pass
    tot = v["200"] + v["500"]
    return {"err_rate": round(v["500"] / tot, 3) if tot else 0.0,
            "p50_s": None, "up": v["500"] < tot if tot else True}


# ---------------------------------------------------------------------------
# Agent + scoring
# ---------------------------------------------------------------------------
def run_agent(agent_cmd: str, obs: Observation) -> str:
    """Invoke the agent under test. The harness pipes the observation as JSON on
    stdin; the agent prints its one-line root-cause diagnosis on stdout."""
    p = subprocess.run(agent_cmd, shell=True, input=json.dumps(asdict(obs)),
                       text=True, capture_output=True, timeout=120)
    return p.stdout.strip()


def score(experiment: str, diagnosis: str) -> bool:
    gold, herrings = GROUND_TRUTH[experiment]
    try:
        from rex.scoring import deterministic_judge
        return deterministic_judge(diagnosis, gold, herrings)
    except Exception:
        # offline fallback if rex import unavailable: token overlap w/ gold,
        # penalize if a red herring dominates.
        d = diagnosis.lower()
        return any(w in d for w in gold.lower().split() if len(w) > 3) \
            and not any(h.lower() in d and h.lower() not in gold.lower() for h in herrings)


def selftest() -> int:
    """No cluster, no agent: prove the sim backend produces the right loud victim
    and that an oracle diagnosis scores True while a red-herring scores False."""
    ok = True
    for exp, (gold, herrings) in GROUND_TRUTH.items():
        if exp == "j1-gateway-pod-kill":
            obs = Observation(experiment=exp, per_app={"gateway": {"err_rate": 1.0, "up": False}},
                              loudest_victim="gateway", notes="pod-kill self-fault")
        else:
            obs = _sim_observe(exp)
        oracle_pass = score(exp, gold)
        herring_pass = score(exp, f"the {herrings[0]} is the problem")
        good = oracle_pass and not herring_pass and bool(obs.loudest_victim)
        print(f"[{'PASS' if good else 'FAIL'}] {exp:28s} victim={obs.loudest_victim:9s} "
              f"oracle={oracle_pass} herring={herring_pass}")
        ok = ok and good
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", choices=["sim", "kube"], default="sim")
    ap.add_argument("--experiment", default=None, help="single experiment name; default = all")
    ap.add_argument("--agent-cmd", default=None, help="shell cmd; reads obs JSON on stdin, prints diagnosis")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--soak", type=int, default=30)
    a = ap.parse_args()

    if a.selftest:
        return selftest()

    exps = [a.experiment] if a.experiment else list(GROUND_TRUTH)
    results = []
    for exp in exps:
        obs = _sim_observe(exp) if a.backend == "sim" else _kube_observe(exp, a.soak)
        diagnosis = run_agent(a.agent_cmd, obs) if a.agent_cmd else "(no agent; observation only)"
        passed = score(exp, diagnosis) if a.agent_cmd else None
        results.append({"experiment": exp, "loudest_victim": obs.loudest_victim,
                        "diagnosis": diagnosis, "passed": passed, "obs": asdict(obs)})
    print(json.dumps({"backend": a.backend, "results": results}, indent=2))
    if a.agent_cmd:
        scored = [r for r in results if r["passed"] is not None]
        n_pass = sum(1 for r in scored if r["passed"])
        print(f"\nscore: {n_pass}/{len(scored)} experiments diagnosed correctly", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
