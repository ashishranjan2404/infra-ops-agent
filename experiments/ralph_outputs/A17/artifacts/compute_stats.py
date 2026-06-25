#!/usr/bin/env python3
"""Re-derive every quantitative claim in DATA_CARD.md straight from disk.

Usage:
    python3 compute_stats.py [--dir scenarios/cidg/generated] [--out stats.json]

Pure stdlib + pyyaml. Exits non-zero if any YAML/JSON fails to parse, so the data
card's numbers can never silently drift onto a corrupt corpus.
"""
from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import sys

import yaml

# A scenario is "postmortem_derived" iff its meta.source names a real org's public
# incident. Synthetic-leaf / synthetic-cascade templates use generic mechanism names
# (e.g. "fd-exhaust-leaf-shipper", "mem-leak-cascade-cache") with NO real org.
_POSTMORTEM_ORGS = (
    "facebook", "cloudflare", "github", "azure", "slack", "knight",
    "datadog", "circleci", "launchdarkly", "mozilla", "firefox", "gitlab",
    "incident.io", "incidentio", "crowdstrike", "railway", "kinesis", "dynamodb",
    "cloudbleed", "travis", "roblox", "fastly", "reddit", "honeycomb",
    "stripe", "monzo", "aws s3", "aws kinesis", "aws dynamodb", "gcp service",
)
# Generic synthetic templates: filename/source contains one of these structural words
# rather than an org name.
_SYNTH_MARKERS = ("leaf", "cascade", "multi-", "-positive", "singleton", "leaf-")


def _provenance(source: str, fname: str = "") -> str:
    s = f"{source} {fname}".lower()
    if any(m in s for m in _SYNTH_MARKERS):
        return "synthetic_leaf"
    return "postmortem_derived" if any(o in s for o in _POSTMORTEM_ORGS) else "synthetic_leaf"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", default="scenarios/cidg/generated")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.dir, "*.yaml")))
    reg_path = os.path.join(args.dir, "registry.json")
    if not files:
        print(f"ERROR: no YAML scenarios under {args.dir}", file=sys.stderr)
        return 2

    registry = json.load(open(reg_path))  # raises -> non-zero exit if corrupt
    reg_names = {os.path.basename(v["path"]) for v in registry.values()}
    yaml_names = {os.path.basename(f) for f in files}

    fc = collections.Counter()
    clouds = collections.Counter()
    chaos = collections.Counter()
    fixes = collections.Counter()
    nodes_hist = collections.Counter()
    prov = collections.Counter()
    thesis = collections.Counter()

    for f in files:
        d = yaml.safe_load(open(f))  # raises -> non-zero exit if corrupt
        m = d["meta"]
        fc[m["failure_class"]] += 1
        for c in m.get("clouds", []):
            clouds[c] += 1
        chaos[d["fault"]["chaos_kind"]] += 1
        nodes_hist[len(d["topology"]["nodes"])] += 1
        prov[_provenance(m.get("source", ""), os.path.basename(f))] += 1
        for step in d.get("canonical_fix", {}).get("steps", []):
            fixes[step["tool"]] += 1
        a = d.get("assertions", {})
        for k in ("cascades", "loudest_alert_not_cause", "buried_gun_exists",
                  "hysteresis", "monitoring_degrades"):
            thesis[k] += bool(a.get(k))
        thesis["with_trap_actions"] += bool(d.get("trap_actions"))

    families = collections.Counter(v.get("family", "?") for v in registry.values())

    import datetime
    out = {
        "snapshot_utc": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "corpus_dir": args.dir,
        "n_yaml": len(files),
        "n_registry": len(registry),
        "yaml_not_in_registry": sorted(yaml_names - reg_names),
        "registry_not_on_disk": sorted(
            os.path.basename(v["path"]) for v in registry.values()
            if not os.path.exists(v["path"])
        ),
        "failure_class": dict(sorted(fc.items())),
        "clouds": dict(sorted(clouds.items())),
        "chaos_kind": dict(chaos),
        "canonical_fix_tools": dict(sorted(fixes.items(), key=lambda kv: -kv[1])),
        "families_registry": dict(families),
        "node_count_hist": {str(k): v for k, v in sorted(nodes_hist.items())},
        "thesis": dict(thesis),
        "provenance": dict(prov),
        "files_counted": sorted(yaml_names),
    }

    # invariant: failure-class counts must sum to scenario count
    assert sum(fc.values()) == len(files), "failure_class counts do not sum to n_yaml"

    text = json.dumps(out, indent=2)
    if args.out:
        open(args.out, "w").write(text + "\n")
    print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
