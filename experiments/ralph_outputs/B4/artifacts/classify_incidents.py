#!/usr/bin/env python3
"""B4 — Classify every CIDG generated incident into simple / cascade / novel.

Reuses the A7 difficulty sidecar and the A8 novelty/family sidecar where present, and falls
back to a deterministic, mechanics-grounded rule for the incidents those sidecars don't cover
(the 80-89 real-outage series + the a11 transfer pairs).

Classification ordering (primary-type rule; see B4/03_improved_plan.md, 04_spec.md):
  1. registry.json family (authoritative for the 32 labelled incidents)        tier=registry
  2. A8 heldout_split.csv family (cross-check / extra coverage)                 tier=a8
  3. filename '-leaf-' -> simple ; '-cascade-' -> cascade (a11 self-describe)   tier=name-rule
  4. meta.source is a dated real-world outage -> novel                         tier=real-outage
  5. assertions.cascades and >1 distinct SLO node -> cascade                   tier=mechanics
  6. else -> simple                                                            tier=mechanics

Read-only. Writes only into B4/artifacts/. No shared core files touched.
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re

try:
    import yaml
except ImportError:  # pragma: no cover
    raise SystemExit("pyyaml required (in requirements-rex.txt): pip install pyyaml")

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
GEN = os.path.join(REPO, "scenarios", "cidg", "generated")
REGISTRY = os.path.join(GEN, "registry.json")
A8_CSV = os.path.join(REPO, "experiments", "ralph_outputs", "A8", "artifacts", "heldout_split.csv")
A7_CSV = os.path.join(REPO, "experiments", "ralph_outputs", "A7", "artifacts", "difficulty_scores.csv")

TYPES = ("simple", "cascade", "novel")
YEAR_RE = re.compile(r"\b(19|20)\d\d\b")


def snake(s: str) -> str:
    return s.strip().lower().replace("-", "_").replace(" ", "_")


def load_registry() -> dict:
    """basename(path) -> family, for the 32 labelled incidents."""
    out = {}
    if not os.path.exists(REGISTRY):
        return out
    reg = json.load(open(REGISTRY))
    for key, v in reg.items():
        if isinstance(v, dict) and "family" in v:
            base = os.path.basename(v.get("path", "")) or None
            if base:
                out[base] = v["family"]
            out[snake(key)] = v["family"]  # also key by snake id
    return out


def load_a8() -> dict:
    out = {}
    if not os.path.exists(A8_CSV):
        return out
    for row in csv.DictReader(open(A8_CSV)):
        out[snake(row["cidg_key"])] = row["family"]
        out[os.path.basename(row.get("yaml", ""))] = row["family"]
    return out


def load_a7() -> dict:
    out = {}
    if not os.path.exists(A7_CSV):
        return out
    for row in csv.DictReader(open(A7_CSV)):
        out[snake(row["id"])] = row.get("difficulty_bucket")
    return out


def n_slo_nodes(doc: dict) -> int:
    slo = doc.get("slo") or []
    return len({s.get("node") for s in slo if isinstance(s, dict)})


def is_real_outage(doc: dict) -> bool:
    src = ((doc.get("meta") or {}).get("source") or "").strip()
    if not src or src.lower().startswith("synthetic"):
        return False
    return bool(YEAR_RE.search(src))


def classify_one(fname: str, doc: dict, reg: dict, a8: dict, a7: dict) -> dict:
    base = os.path.basename(fname)
    iid = (doc.get("meta") or {}).get("id") or base.removesuffix(".yaml")
    sid = snake(iid)
    diff = a7.get(sid)

    def rec(t, tier):
        return {"file": base, "incident_id": iid, "type": t,
                "source_tier": tier, "difficulty": diff}

    # 1) registry (authoritative)
    if base in reg:
        return rec(reg[base], "registry")
    if sid in reg:
        return rec(reg[sid], "registry")
    # 2) A8 sidecar
    if base in a8:
        return rec(a8[base], "a8")
    if sid in a8:
        return rec(a8[sid], "a8")
    # 3) a11 self-describing filenames
    if "-leaf-" in base:
        return rec("simple", "name-rule")
    if "-cascade-" in base:
        return rec("cascade", "name-rule")
    # 4) dated real-world outage -> novel substrate
    if is_real_outage(doc):
        return rec("novel", "real-outage")
    # 5) mechanics: cascade vs simple
    cascades = bool((doc.get("assertions") or {}).get("cascades"))
    if cascades and n_slo_nodes(doc) > 1:
        return rec("cascade", "mechanics")
    return rec("simple", "mechanics")


def main() -> None:
    reg, a8, a7 = load_registry(), load_a8(), load_a7()
    files = sorted(glob.glob(os.path.join(GEN, "*.yaml")))
    rows = []
    for f in files:
        try:
            doc = yaml.safe_load(open(f)) or {}
        except yaml.YAMLError as e:  # pragma: no cover
            print(f"  WARN: could not parse {f}: {e}")
            continue
        rows.append(classify_one(f, doc, reg, a8, a7))

    by_type = {t: sum(1 for r in rows if r["type"] == t) for t in TYPES}
    by_tier = {}
    for r in rows:
        by_tier[r["source_tier"]] = by_tier.get(r["source_tier"], 0) + 1

    out_json = {
        "schema": {
            "type": "simple|cascade|novel  (primary-type: novel>cascade>simple)",
            "source_tier": "registry|a8|name-rule|real-outage|mechanics",
            "difficulty": "A7 bucket easy|medium|hard if id matched, else null",
        },
        "count": len(rows),
        "by_type": by_type,
        "by_source_tier": by_tier,
        "incidents": sorted(rows, key=lambda r: (r["type"], r["file"])),
    }
    jpath = os.path.join(HERE, "incident_types.json")
    cpath = os.path.join(HERE, "incident_types.csv")
    json.dump(out_json, open(jpath, "w"), indent=1)
    with open(cpath, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["file", "incident_id", "type", "source_tier", "difficulty"])
        for r in sorted(rows, key=lambda r: (r["type"], r["file"])):
            w.writerow([r["file"], r["incident_id"], r["type"], r["source_tier"],
                        r["difficulty"] or ""])

    print(f"classified {len(rows)} incidents -> {by_type}")
    print(f"by source tier: {by_tier}")
    print(f"wrote {os.path.relpath(jpath, REPO)} and {os.path.relpath(cpath, REPO)}")


if __name__ == "__main__":
    main()
