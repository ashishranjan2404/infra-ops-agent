#!/usr/bin/env python3
"""Noisy-metrics transform — degrade alerting/observability in a CIDG scenario.

This is a *spec-level* transform: given a baseline scenario YAML (the
single source of truth consumed by both the Tier-A sim and the live mesh),
it produces a NEW scenario where the monitoring/alerting layer degrades while
the underlying physics (topology + root cause + canonical fix) is unchanged.

It targets exactly the fields the assertion schema already reserves for this:
  observation.alerting            : "uniform" -> "noisy"
  observation.monitoring_degrades : False     -> True
  observation.smoking_guns[*].buried_under    : scaled up (alert storm)
  assertions.monitoring_degrades  : False     -> True

To keep `assertions.monitoring_degrades=True` valid (sim/spec.py:350 requires
an 'observes' edge), the transform injects a `monitoring` node and an
`observes` edge from it to the root-cause node's blast radius IF the scenario
has none. It never edits the original file in place — it writes a new YAML.

Usage:
    python noisy_metrics_transform.py <baseline.yaml> -o <out.yaml>
    python noisy_metrics_transform.py <baseline.yaml> --check   # validate only

The output is itself a valid ScenarioSpec (round-trips through sim.spec.load_spec
+ validate with zero errors), so it is a drop-in scenario, not a sidecar config.
"""
from __future__ import annotations

import argparse
import copy
import sys
from typing import Any

import yaml

# How much louder the alert storm gets: every buried smoking gun is buried under
# `BURIED_MULT`x more noise lines, with a floor so even un-buried guns get noise.
BURIED_MULT = 3
BURIED_FLOOR = 20

MONITOR_NODE = "monitoring-stack"


def _root_node(doc: dict) -> str:
    """The node the root cause lives on (head of an 'A->B' edge location)."""
    loc = doc["root_cause"]["location"]
    return loc.split("->")[0].strip() if "->" in loc else loc.strip()


def _node_names(doc: dict) -> set:
    return {n["name"] for n in doc.get("topology", {}).get("nodes", [])}


def _ensure_observes_edge(doc: dict) -> bool:
    """Guarantee at least one 'observes' edge so monitoring_degrades is schema-valid.
    Returns True if the topology was modified."""
    topo = doc.setdefault("topology", {})
    edges = topo.setdefault("edges", [])
    if any(e.get("type") == "observes" for e in edges):
        return False
    nodes = topo.setdefault("nodes", [])
    names = _node_names(doc)
    # Add a monitoring node iff missing, then observe the root-cause node: when the
    # root node is in the blast radius, observation itself degrades.
    if MONITOR_NODE not in names:
        nodes.append({"name": MONITOR_NODE, "kind": "monitoring",
                      "resources": {"replicas": 1}})
    edges.append({"from": MONITOR_NODE, "to": _root_node(doc),
                  "type": "observes", "weight": 1.0})
    return True


def transform(doc: dict) -> dict:
    """Return a NEW degraded-alerting scenario dict. Pure: input is not mutated."""
    out = copy.deepcopy(doc)

    # 1. Re-id so the variant is a distinct scenario, not a silent overwrite.
    meta = out.setdefault("meta", {})
    base_id = meta.get("id", "scenario")
    if not base_id.endswith("-noisy"):
        meta["id"] = f"{base_id}-noisy"
    meta["title"] = f"{meta.get('title', base_id)} (noisy metrics / alerting degrades)"
    meta["derived_from"] = base_id
    meta["variant"] = "noisy_metrics"

    # 2. Degrade the observation layer.
    obs = out.setdefault("observation", {})
    obs["alerting"] = "noisy"
    obs["monitoring_degrades"] = True
    for g in obs.get("smoking_guns", []) or []:
        cur = int(g.get("buried_under", 0))
        g["buried_under"] = max(cur * BURIED_MULT, BURIED_FLOOR)

    # 3. Make monitoring_degrades structurally valid (needs an 'observes' edge).
    _ensure_observes_edge(out)

    # 4. Flip the corresponding assertion so tooling enforces the property.
    asrt = out.setdefault("assertions", {})
    asrt["monitoring_degrades"] = True

    return out


def _validate(doc: dict) -> list:
    """Round-trip the dict through the real spec loader + validator."""
    try:
        import os
        # Repo root = three levels up from this file
        # (experiments/ralph_outputs/A15/artifacts/). Add it so `sim` imports
        # regardless of the caller's cwd / PYTHONPATH.
        root = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
        if root not in sys.path:
            sys.path.insert(0, root)
        import sim.spec as spec_mod  # late import: only needed when validating
    except Exception as e:  # noqa: BLE001
        return [f"could not import sim.spec for validation: {e}"]
    spec = spec_mod._spec_from_dict(doc)
    return spec_mod.validate(spec)


def main(argv: list) -> int:
    ap = argparse.ArgumentParser(description="Inject metric noise / alert degradation.")
    ap.add_argument("baseline", help="path to a baseline scenario YAML")
    ap.add_argument("-o", "--out", help="output YAML path (default: stdout)")
    ap.add_argument("--check", action="store_true",
                    help="validate the transformed spec and report, don't write")
    args = ap.parse_args(argv)

    with open(args.baseline) as f:
        doc = yaml.safe_load(f)

    out_doc = transform(doc)
    errs = _validate(out_doc)
    if errs:
        print(f"INVALID transformed spec ({len(errs)} errors):", file=sys.stderr)
        for e in errs:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK  transformed [{out_doc['meta']['id']}] validates clean "
          f"(alerting=noisy, monitoring_degrades=True)", file=sys.stderr)

    if args.check:
        return 0

    text = yaml.safe_dump(out_doc, sort_keys=False)
    if args.out:
        with open(args.out, "w") as f:
            f.write(text)
        print(f"wrote {args.out}", file=sys.stderr)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
