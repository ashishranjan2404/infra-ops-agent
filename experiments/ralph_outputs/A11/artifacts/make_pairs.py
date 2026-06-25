#!/usr/bin/env python3
"""A11 — generate transfer-test incident PAIRS.

Each pair shares the SAME root cause (failure_class + root kind + canonical fix
tool) but presents a DIFFERENT surface symptom: different topology, different
service names, different SLO-violating node, different smoking-gun phrasing, and
in most pairs a leaf-vs-cascade structural difference.

The point: an agent that has learned the *mechanism* (not the surface) should
solve B given A. We hold the fix invariant; we vary everything observable.

Writes 6 YAMLs into scenarios/cidg/generated/ (numbers 80-85, verified unused)
and a pairs_manifest.json mapping A<->B and asserting the shared root cause.
"""
import json
import os
import sys

import yaml

REPO = "/Users/mei/rl"
GEN = os.path.join(REPO, "scenarios", "cidg", "generated")
ART = os.path.join(REPO, "experiments", "ralph_outputs", "A11", "artifacts")


def leaf_node(name, kind="service", replicas=2):
    return {"name": name, "kind": kind, "resources": {"replicas": replicas}}


def scenario(*, sid, title, failure_class, nodes, edges, root_loc,
             root_hidden, smoking_guns, slo, trap_actions, fix_tool,
             fix_args, cascades, loudest_not_cause, buried_gun, seed):
    """Build one scenario dict in the established schema."""
    return {
        "meta": {
            "id": sid,
            "title": title,
            "source": title,
            "urls": [],
            "failure_class": failure_class,
            "clouds": ["gke", "lke"],
        },
        "topology": {"nodes": nodes, "edges": edges},
        "root_cause": {
            "location": root_loc,
            "kind": failure_class,
            "severity": 0.7,
            "hidden": root_hidden,
            "persistent": False,
            "reset_by": [],
        },
        "fault": {
            "chaos_kind": "exec",
            "exec_cmd": f"inject {failure_class} on {root_loc}",
            "sim": {"set": {f"{failure_class}_active": True}},
            "duration_s": 120,
        },
        "observation": {
            "alerting": "uniform",
            "monitoring_degrades": False,
            "smoking_guns": smoking_guns,
        },
        "slo": slo,
        "trap_actions": trap_actions,
        "canonical_fix": {
            "ordering_notes": f"Fix the root '{root_loc}' with {fix_tool}.",
            "steps": [{"tool": fix_tool, "args": {"target": root_loc, **fix_args}}],
        },
        "assertions": {
            "cascades": cascades,
            "loudest_alert_not_cause": loudest_not_cause,
            "fix_resolves": True,
            "buried_gun_exists": buried_gun,
            "hysteresis": False,
            "monitoring_degrades": False,
        },
        "chance": {"flap_prob": 0.05, "jitter": 0.03, "partial_recovery_prob": 0.0},
        "seed": seed,
    }


# ---------------------------------------------------------------------------
# PAIR 1 — root cause: fd_exhaust, fix: restart_service
#   A: simple leaf (file-descriptor exhaustion on a log shipper) — symptom is
#      the shipper itself erroring.
#   B: cascade (same fd_exhaust on a gateway) — symptom is two *downstream*
#      services breaching SLO while the root gateway looks healthy.
# ---------------------------------------------------------------------------
p1a = scenario(
    sid="fd-exhaust-leaf-shipper",
    title="PAIR1-A fd_exhaust leaf: log shipper file-descriptor exhaustion",
    failure_class="fd_exhaust",
    nodes=[leaf_node("log-shipper", "service", 2)],
    edges=[],
    root_loc="log-shipper",
    root_hidden=False,
    smoking_guns=[],
    slo=[{"metric": "error_rate_pct", "node": "log-shipper",
          "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3}],
    trap_actions=[{"tool": "scale_deployment", "args": {"target": "log-shipper"}}],
    fix_tool="restart_service", fix_args={}, cascades=False,
    loudest_not_cause=False, buried_gun=False, seed=1080,
)
p1b = scenario(
    sid="fd-exhaust-cascade-gw",
    title="PAIR1-B fd_exhaust cascade: API gateway socket exhaustion starves callers",
    failure_class="fd_exhaust",
    nodes=[
        leaf_node("api-gw", "lb", 4),
        leaf_node("orders-svc", "service", 3),
        leaf_node("notify-svc", "service", 3),
    ],
    edges=[
        {"from": "orders-svc", "to": "api-gw", "type": "required", "weight": 1.0,
         "latency_add_ms": 5, "retry": 0.3},
        {"from": "notify-svc", "to": "api-gw", "type": "required", "weight": 1.0,
         "latency_add_ms": 5, "retry": 0.3},
    ],
    root_loc="api-gw",
    root_hidden=True,
    smoking_guns=[{"tool": "get_logs", "node": "api-gw",
                   "signature": "fd-exhaust-cascade-gw: root fault on api-gw",
                   "buried_under": 40}],
    slo=[
        {"metric": "error_rate_pct", "node": "orders-svc",
         "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3},
        {"metric": "error_rate_pct", "node": "notify-svc",
         "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3},
    ],
    trap_actions=[{"tool": "scale_deployment",
                   "args": {"target": "orders-svc", "replicas": 8}}],
    fix_tool="restart_service", fix_args={}, cascades=True,
    loudest_not_cause=True, buried_gun=True, seed=1081,
)

# ---------------------------------------------------------------------------
# PAIR 2 — root cause: cert_expire, fix: renew_certificate
#   A: leaf — an mTLS sidecar's cert expired, the service itself rejects calls.
#   B: cascade — an expired ingress TLS cert; symptom is a *web frontend* and a
#      *mobile-bff* both 5xx-ing while the ingress is the buried root.
# ---------------------------------------------------------------------------
p2a = scenario(
    sid="cert-expire-leaf-sidecar",
    title="PAIR2-A cert_expire leaf: payments sidecar mTLS cert expired",
    failure_class="cert_expire",
    nodes=[leaf_node("payments-svc", "service", 2)],
    edges=[],
    root_loc="payments-svc",
    root_hidden=False,
    smoking_guns=[],
    slo=[{"metric": "error_rate_pct", "node": "payments-svc",
          "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3}],
    trap_actions=[{"tool": "restart_service", "args": {"target": "payments-svc"}}],
    fix_tool="renew_certificate", fix_args={}, cascades=False,
    loudest_not_cause=False, buried_gun=False, seed=1082,
)
p2b = scenario(
    sid="cert-expire-cascade-ingress",
    title="PAIR2-B cert_expire cascade: ingress TLS cert expired, frontends 5xx",
    failure_class="cert_expire",
    nodes=[
        leaf_node("tls-ingress", "lb", 3),
        leaf_node("web-frontend", "service", 3),
        leaf_node("mobile-bff", "service", 3),
    ],
    edges=[
        {"from": "web-frontend", "to": "tls-ingress", "type": "required",
         "weight": 1.0, "latency_add_ms": 5, "retry": 0.3},
        {"from": "mobile-bff", "to": "tls-ingress", "type": "required",
         "weight": 1.0, "latency_add_ms": 5, "retry": 0.3},
    ],
    root_loc="tls-ingress",
    root_hidden=True,
    smoking_guns=[{"tool": "get_logs", "node": "tls-ingress",
                   "signature": "cert-expire-cascade-ingress: root fault on tls-ingress",
                   "buried_under": 40}],
    slo=[
        {"metric": "error_rate_pct", "node": "web-frontend",
         "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3},
        {"metric": "error_rate_pct", "node": "mobile-bff",
         "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3},
    ],
    trap_actions=[{"tool": "rollback_deployment",
                   "args": {"target": "web-frontend"}}],
    fix_tool="renew_certificate", fix_args={}, cascades=True,
    loudest_not_cause=True, buried_gun=True, seed=1083,
)

# ---------------------------------------------------------------------------
# PAIR 3 — root cause: mem_leak, fix: increase_memory_limit
#   A: leaf — a media transcoder leaks heap and OOMs itself.
#   B: cascade — a shared cache layer leaks; the symptom surfaces as a
#      *catalog-api* and *recsys* degrading (origin overload from cache OOM).
# ---------------------------------------------------------------------------
p3a = scenario(
    sid="mem-leak-leaf-transcoder",
    title="PAIR3-A mem_leak leaf: media transcoder heap leak OOMs",
    failure_class="mem_leak",
    nodes=[leaf_node("transcoder", "service", 2)],
    edges=[],
    root_loc="transcoder",
    root_hidden=False,
    smoking_guns=[],
    slo=[{"metric": "error_rate_pct", "node": "transcoder",
          "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3}],
    trap_actions=[{"tool": "scale_deployment", "args": {"target": "transcoder"}}],
    fix_tool="increase_memory_limit", fix_args={}, cascades=False,
    loudest_not_cause=False, buried_gun=False, seed=1084,
)
p3b = scenario(
    sid="mem-leak-cascade-cache",
    title="PAIR3-B mem_leak cascade: cache tier heap leak overloads origin services",
    failure_class="mem_leak",
    nodes=[
        leaf_node("object-cache", "datastore", 3),
        leaf_node("catalog-api", "service", 3),
        leaf_node("recsys", "service", 3),
    ],
    edges=[
        {"from": "catalog-api", "to": "object-cache", "type": "required",
         "weight": 1.0, "latency_add_ms": 5, "retry": 0.3},
        {"from": "recsys", "to": "object-cache", "type": "required",
         "weight": 1.0, "latency_add_ms": 5, "retry": 0.3},
    ],
    root_loc="object-cache",
    root_hidden=True,
    smoking_guns=[{"tool": "get_logs", "node": "object-cache",
                   "signature": "mem-leak-cascade-cache: root fault on object-cache",
                   "buried_under": 40}],
    slo=[
        {"metric": "error_rate_pct", "node": "catalog-api",
         "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3},
        {"metric": "error_rate_pct", "node": "recsys",
         "direction": "higher_bad", "threshold": 5, "sustain_ticks": 3},
    ],
    trap_actions=[{"tool": "scale_deployment",
                   "args": {"target": "catalog-api", "replicas": 8}}],
    fix_tool="increase_memory_limit", fix_args={}, cascades=True,
    loudest_not_cause=True, buried_gun=True, seed=1085,
)

# Task-namespaced filenames (prefix a11-pair-) to avoid number collisions with
# other parallel Ralph workers that also claimed numbers 80-89.
FILES = {
    "a11-pair-fd-exhaust-leaf-shipper.yaml": p1a,
    "a11-pair-fd-exhaust-cascade-gw.yaml": p1b,
    "a11-pair-cert-expire-leaf-sidecar.yaml": p2a,
    "a11-pair-cert-expire-cascade-ingress.yaml": p2b,
    "a11-pair-mem-leak-leaf-transcoder.yaml": p3a,
    "a11-pair-mem-leak-cascade-cache.yaml": p3b,
}

PAIRS = [
    {"pair_id": "P1", "shared_root_cause": {"failure_class": "fd_exhaust",
        "fix_tool": "restart_service"},
     "A": "a11-pair-fd-exhaust-leaf-shipper.yaml", "B": "a11-pair-fd-exhaust-cascade-gw.yaml",
     "symptom_A": "the log-shipper service itself errors out (leaf, root visible)",
     "symptom_B": "two downstream callers (orders-svc, notify-svc) breach SLO while the api-gw root is buried (cascade)"},
    {"pair_id": "P2", "shared_root_cause": {"failure_class": "cert_expire",
        "fix_tool": "renew_certificate"},
     "A": "a11-pair-cert-expire-leaf-sidecar.yaml", "B": "a11-pair-cert-expire-cascade-ingress.yaml",
     "symptom_A": "payments-svc rejects its own calls (leaf, root visible)",
     "symptom_B": "web-frontend and mobile-bff both 5xx while tls-ingress is the buried root (cascade)"},
    {"pair_id": "P3", "shared_root_cause": {"failure_class": "mem_leak",
        "fix_tool": "increase_memory_limit"},
     "A": "a11-pair-mem-leak-leaf-transcoder.yaml", "B": "a11-pair-mem-leak-cascade-cache.yaml",
     "symptom_A": "transcoder OOMs itself (leaf, root visible)",
     "symptom_B": "catalog-api and recsys degrade from origin overload while object-cache is the buried root (cascade)"},
]


def main():
    # Safety: refuse to overwrite any existing file.
    for fn in FILES:
        p = os.path.join(GEN, fn)
        if os.path.exists(p):
            print(f"REFUSING: {fn} already exists", file=sys.stderr)
            sys.exit(1)

    written = []
    for fn, obj in FILES.items():
        p = os.path.join(GEN, fn)
        with open(p, "w") as f:
            yaml.safe_dump(obj, f, sort_keys=False, default_flow_style=False)
        # parse-check round trip
        with open(p) as f:
            back = yaml.safe_load(f)
        assert back["meta"]["failure_class"] == obj["meta"]["failure_class"]
        assert back["canonical_fix"]["steps"][0]["tool"] == \
            obj["canonical_fix"]["steps"][0]["tool"]
        written.append(fn)
        print(f"wrote+parsed {fn}")

    # Invariant check: each pair shares failure_class AND fix tool, but differs
    # in topology node count (symptom).
    for pr in PAIRS:
        a = FILES[pr["A"]]
        b = FILES[pr["B"]]
        assert a["meta"]["failure_class"] == b["meta"]["failure_class"] == \
            pr["shared_root_cause"]["failure_class"]
        assert a["canonical_fix"]["steps"][0]["tool"] == \
            b["canonical_fix"]["steps"][0]["tool"] == \
            pr["shared_root_cause"]["fix_tool"]
        assert len(a["topology"]["nodes"]) != len(b["topology"]["nodes"]), \
            "pair must differ in surface symptom"
        print(f"pair {pr['pair_id']} OK: shared root="
              f"{pr['shared_root_cause']['failure_class']}/"
              f"{pr['shared_root_cause']['fix_tool']}")

    manifest = {
        "description": "A11 transfer-test incident pairs. Each pair shares root "
                       "cause (failure_class + canonical fix tool) but differs in "
                       "surface symptom (leaf-visible vs buried cascade, different "
                       "topology and service names). Use A as train, B as held-out "
                       "transfer test (or vice versa).",
        "generated_dir": "scenarios/cidg/generated/",
        "pairs": PAIRS,
        "files": written,
    }
    mpath = os.path.join(GEN, "a11_pairs_manifest.json")
    with open(mpath, "w") as f:
        json.dump(manifest, f, indent=2)
    # also drop a copy into artifacts for the record
    with open(os.path.join(ART, "pairs_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    print(f"wrote manifest {mpath}")


if __name__ == "__main__":
    main()
