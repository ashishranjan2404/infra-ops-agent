#!/usr/bin/env python3
"""A10 — Blast-radius metadata for CIDG incidents.

Derives, for each scenario YAML in scenarios/cidg/generated/, the set of
services affected by the root-cause fault by propagating along the dependency
topology, then emits a sidecar blast_radius.json and blast_radius.csv.

Edge semantics (validated against the YAMLs):
  An edge {from: A, to: B, type: required} means "A depends on B" (A calls B).
  Therefore a fault at node N propagates to every node that (transitively)
  *depends on* N, i.e. we walk edges in the reverse direction (to -> from).

Severity tier is derived from blast count + root_cause.severity + whether the
scenario asserts a cascade. Tiers: SEV1 (>=4 services or sev>=0.9 cascade),
SEV2 (>=2 services or cascade), SEV3 (single service, contained).

This script reads only; it does NOT modify any YAML or shared core file.
"""
from __future__ import annotations
import csv
import glob
import json
import os
import sys
from collections import defaultdict, deque

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
SCEN_GLOB = os.path.join(REPO_ROOT, "scenarios", "cidg", "generated", "*.yaml")
OUT_DIR = os.path.join(os.path.dirname(__file__))


def load_yaml(path):
    import yaml
    with open(path) as fh:
        return yaml.safe_load(fh)


def reverse_reachable(root, edges):
    """Nodes reachable from `root` by following edges in reverse (to->from).

    edges: list of (from_node, to_node). A 'from' depends on 'to', so impact
    flows to->from. Returns the set of affected dependents INCLUDING root.
    """
    rev = defaultdict(list)
    for fr, to in edges:
        rev[to].append(fr)
    seen = {root}
    q = deque([root])
    while q:
        cur = q.popleft()
        for nxt in rev.get(cur, []):
            if nxt not in seen:
                seen.add(nxt)
                q.append(nxt)
    return seen


def severity_tier(n_affected, rc_sev, cascades):
    if n_affected >= 4 or (rc_sev >= 0.9 and cascades):
        return "SEV1"
    if n_affected >= 2 or cascades:
        return "SEV2"
    return "SEV3"


def compute_for_scenario(path):
    d = load_yaml(path)
    topo = d.get("topology", {}) or {}
    nodes = [n["name"] for n in (topo.get("nodes") or [])]
    node_set = set(nodes)
    edges = []
    for e in (topo.get("edges") or []):
        fr, to = e.get("from"), e.get("to")
        if fr in node_set and to in node_set:
            edges.append((fr, to))

    rc = d.get("root_cause", {}) or {}
    root = rc.get("location")
    rc_sev = float(rc.get("severity", 0.0) or 0.0)
    cascades = bool((d.get("assertions", {}) or {}).get("cascades", False))

    if root in node_set:
        affected = sorted(reverse_reachable(root, edges))
    elif root:
        affected = [root]
    else:
        affected = []

    incident_id = (d.get("meta", {}) or {}).get("id") or os.path.splitext(os.path.basename(path))[0]
    n = len(affected)
    tier = severity_tier(n, rc_sev, cascades)
    return {
        "incident_id": incident_id,
        "file": os.path.relpath(path, REPO_ROOT),
        "root_cause_node": root,
        "root_cause_severity": rc_sev,
        "cascades": cascades,
        "total_services": len(nodes),
        "services_affected": n,
        "services_affected_pct": round(100.0 * n / len(nodes), 1) if nodes else 0.0,
        "affected_services": affected,
        "severity_tier": tier,
    }


def main():
    files = sorted(glob.glob(SCEN_GLOB))
    if not files:
        print(f"No scenarios found at {SCEN_GLOB}", file=sys.stderr)
        return 1
    rows = [compute_for_scenario(f) for f in files]

    json_path = os.path.join(OUT_DIR, "blast_radius.json")
    with open(json_path, "w") as fh:
        json.dump({"count": len(rows), "incidents": rows}, fh, indent=2)

    csv_path = os.path.join(OUT_DIR, "blast_radius.csv")
    with open(csv_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow([
            "incident_id", "root_cause_node", "total_services",
            "services_affected", "services_affected_pct",
            "severity_tier", "cascades", "affected_services",
        ])
        for r in rows:
            w.writerow([
                r["incident_id"], r["root_cause_node"], r["total_services"],
                r["services_affected"], r["services_affected_pct"],
                r["severity_tier"], r["cascades"], "|".join(r["affected_services"]),
            ])

    tiers = defaultdict(int)
    for r in rows:
        tiers[r["severity_tier"]] += 1
    print(f"Processed {len(rows)} incidents")
    print(f"  wrote {os.path.relpath(json_path, REPO_ROOT)}")
    print(f"  wrote {os.path.relpath(csv_path, REPO_ROOT)}")
    print(f"  tier distribution: {dict(sorted(tiers.items()))}")
    multi = sum(1 for r in rows if r["services_affected"] > 1)
    print(f"  multi-service blast: {multi}/{len(rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
