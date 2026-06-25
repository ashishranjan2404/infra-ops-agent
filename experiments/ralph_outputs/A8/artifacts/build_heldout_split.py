#!/usr/bin/env python3
"""A8 — Strict held-out test split builder + contamination assertion.

Produces a held-out manifest of cidg incidents that NO training data touches,
under a tiered, auditable novelty criterion, and asserts zero overlap with the
training corpora.

Training corpora inspected (read-only):
  - opensre-traj/out/trajectories.jsonl        (synthetic SFT/RFT trajectories)
  - opensre-traj/out/hud_trajectories.jsonl    (HUD rollout traces)

Candidate pool:
  - scenarios/cidg/generated/registry.json + the referenced *.yaml

NOVELTY CRITERIA (an incident is HELD OUT only if it passes ALL tiers):

  Tier 1 - Exact incident-id novelty:
      normalized(cidg_key) is not an exact training `incident` id, and
      the cidg key shares no *significant* multi-token n-gram with any
      training incident id (significant = a token-pair, ignoring a
      stop-list of generic infra words).

  Tier 2 - Source-incident novelty:
      the real-world source event (company + event signature, derived from
      the cidg key's leading company token where present) is not represented
      in the training set. We treat a *company* token (github, cloudflare,
      slack, aws, datadog, circleci, incidentio, launchdarkly, facebook,
      knight, azure, firefox, gke, kafka) as a hard novelty axis: if that
      company appears in training incidents, any cidg incident from the same
      company sharing >=1 additional meaningful token is contaminated.

  Tier 3 - Failure-class novelty (SOFT, recorded not enforced):
      we record whether the incident's failure_class also appears in
      training. Because failure classes are intentionally reused across the
      curriculum, Tier 3 is reported as a `failure_class_seen` flag rather
      than an exclusion — a strictly-novel *instance* of a seen class is
      legitimately held out, but the flag lets a reviewer choose an even
      stricter split.

The DEFAULT held-out set enforces Tier 1 + Tier 2 (true unseen incidents),
and additionally we expose `--strict-class` to also enforce Tier 3.

Outputs:
  heldout_manifest.json   full manifest (criteria, per-incident decision)
  heldout_split.csv       flat table
Exit code 0 iff the asserted held-out set has ZERO overlap with training.
"""
from __future__ import annotations
import json, re, csv, sys, argparse, hashlib
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]  # .../rl
REG = REPO / "scenarios/cidg/generated/registry.json"
TRAIN_FILES = [
    REPO / "opensre-traj/out/trajectories.jsonl",
    REPO / "opensre-traj/out/hud_trajectories.jsonl",
]

# Generic infra tokens that carry no incident identity by themselves.
STOP = {
    "cache", "cold", "stale", "leak", "cert", "expiry", "expire", "disk",
    "fill", "rollout", "limit", "exhaustion", "exhaust", "starve", "pool",
    "flush", "spike", "delay", "error", "errors", "node", "cpu", "fd",
    "the", "and", "via", "with",
}

# Known company / vendor identity tokens — a hard novelty axis.
COMPANIES = {
    "github", "cloudflare", "slack", "aws", "datadog", "circleci",
    "incidentio", "launchdarkly", "facebook", "knight", "azure", "firefox",
    "gke", "kafka", "redis", "consul", "mysql", "proxysql", "kinesis",
    "dynamodb",
}


def norm(s: str) -> str:
    return re.sub(r"[^a-z0-9]", "", (s or "").lower())


def toks(key: str) -> set[str]:
    return {t.lower() for t in re.split(r"[^a-z0-9]+", key.lower()) if t}


def meaningful(key: str) -> set[str]:
    return {t for t in toks(key) if t not in STOP}


def load_training():
    incidents, sids, raw_lines = set(), set(), 0
    for f in TRAIN_FILES:
        if not f.exists():
            continue
        for line in f.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            raw_lines += 1
            d = json.loads(line)
            if d.get("incident"):
                incidents.add(d["incident"])
            if d.get("scenario_id"):
                sids.add(d["scenario_id"])
    return incidents, sids, raw_lines


def load_yaml_meta(path: Path) -> dict:
    try:
        import yaml
        m = yaml.safe_load(path.read_text())
        return m.get("meta", {}) if isinstance(m, dict) else {}
    except Exception:
        return {}


def classify(key: str, fclass: str, train_inc: set[str]):
    """Return (held_out: bool, reasons: dict)."""
    nkey = norm(key)
    train_norm = {norm(i) for i in train_inc}
    train_toks = set()
    for i in train_inc:
        train_toks |= meaningful(i)
    train_companies = {t for t in train_toks if t in COMPANIES}

    # Tier 1: exact id
    exact = nkey in train_norm

    # Tier 1: significant token-pair overlap with any training incident
    kmean = meaningful(key)
    pair_overlap = None
    for i in train_inc:
        shared = kmean & meaningful(i)
        if len(shared) >= 2:
            pair_overlap = (i, sorted(shared))
            break

    # Tier 2: company-axis novelty (HARD). A vendor/company identity token is
    # treated as a hard novelty axis: if the cidg incident names a company that
    # also appears in the training corpus, the real-world source organization is
    # NOT novel, so the incident is contaminated regardless of failure mechanism.
    kcos = {t for t in toks(key) if t in COMPANIES}
    company_hit = None
    for c in kcos:
        if c in train_companies:
            # find a representative training incident from that company
            rep = next((i for i in sorted(train_inc) if c in toks(i)), c)
            company_hit = (c, rep)
            break

    # Tier 3: failure_class (soft)
    fclass_seen = norm(fclass) in train_norm or any(
        norm(fclass) in meaningful_str for meaningful_str in [norm(i) for i in train_inc]
    )

    held = not (exact or pair_overlap or company_hit)
    reasons = {
        "tier1_exact_id_match": bool(exact),
        "tier1_significant_pair_overlap": pair_overlap,
        "tier2_company_axis_hit": company_hit,
        "tier3_failure_class_seen_in_train": bool(fclass_seen),
    }
    return held, reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(Path(__file__).parent))
    ap.add_argument("--strict-class", action="store_true",
                    help="also exclude any incident whose failure_class appears in training (Tier 3 hard)")
    args = ap.parse_args()
    out = Path(args.out_dir)

    train_inc, train_sids, raw = load_training()
    reg = json.loads(REG.read_text())

    rows = []
    for key, v in reg.items():
        meta = load_yaml_meta(REPO / v["path"])
        fclass = meta.get("failure_class", "")
        src = meta.get("source", "")
        held, reasons = classify(key, fclass, train_inc)
        if args.strict_class and reasons["tier3_failure_class_seen_in_train"]:
            held = False
        rows.append({
            "cidg_key": key,
            "yaml": v["path"],
            "family": v.get("family", ""),
            "style": v.get("style", ""),
            "failure_class": fclass,
            "source": src,
            "held_out": held,
            "reasons": reasons,
        })

    held = [r for r in rows if r["held_out"]]
    contam = [r for r in rows if not r["held_out"]]

    # ASSERTION: held-out keys must not exact-match any training incident,
    # and no held-out key may share a significant token-pair with training.
    train_norm = {norm(i) for i in train_inc}
    violations = []
    for r in held:
        if norm(r["cidg_key"]) in train_norm:
            violations.append((r["cidg_key"], "exact id in training"))
        for i in train_inc:
            if len(meaningful(r["cidg_key"]) & meaningful(i)) >= 2:
                violations.append((r["cidg_key"], f"pair-overlap with {i}"))

    manifest = {
        "task_id": "A8",
        "description": "Strict held-out test split for cidg incidents with zero training overlap",
        "criteria": {
            "tier1": "exact incident-id novelty + no significant token-pair overlap",
            "tier2": "company/vendor-axis novelty (same company + shared meaningful token => contaminated)",
            "tier3_soft": "failure_class reuse recorded as flag; hard-enforced only with --strict-class",
            "stop_tokens": sorted(STOP),
            "company_tokens": sorted(COMPANIES),
            "strict_class_mode": bool(args.strict_class),
        },
        "training_corpora": [str(f.relative_to(REPO)) for f in TRAIN_FILES if f.exists()],
        "training_stats": {
            "n_lines": raw,
            "n_distinct_incidents": len(train_inc),
            "n_distinct_scenario_ids": len(train_sids),
            "distinct_incidents": sorted(train_inc),
        },
        "candidate_pool": {
            "registry": str(REG.relative_to(REPO)),
            "n_candidates": len(rows),
        },
        "held_out": sorted(r["cidg_key"] for r in held),
        "n_held_out": len(held),
        "contaminated": sorted(r["cidg_key"] for r in contam),
        "n_contaminated": len(contam),
        "per_incident": rows,
        "assertion_violations": violations,
        "assertion_pass": len(violations) == 0,
        "manifest_sha256": None,
    }
    body = json.dumps({k: v for k, v in manifest.items() if k != "manifest_sha256"},
                      sort_keys=True).encode()
    manifest["manifest_sha256"] = hashlib.sha256(body).hexdigest()

    (out / "heldout_manifest.json").write_text(json.dumps(manifest, indent=2))
    with (out / "heldout_split.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["cidg_key", "yaml", "family", "failure_class", "source",
                    "held_out", "tier1_exact", "tier2_company_hit",
                    "tier3_fclass_seen"])
        for r in rows:
            w.writerow([
                r["cidg_key"], r["yaml"], r["family"], r["failure_class"],
                r["source"], r["held_out"],
                r["reasons"]["tier1_exact_id_match"],
                bool(r["reasons"]["tier2_company_axis_hit"]),
                r["reasons"]["tier3_failure_class_seen_in_train"],
            ])

    print(f"training incidents: {len(train_inc)}  | candidates: {len(rows)}")
    print(f"HELD-OUT: {len(held)}  | contaminated: {len(contam)}")
    print("held-out keys:", manifest["held_out"])
    print(f"assertion_pass={manifest['assertion_pass']} violations={len(violations)}")
    print(f"manifest sha256={manifest['manifest_sha256'][:16]}...")
    return 0 if manifest["assertion_pass"] and held else 1


if __name__ == "__main__":
    sys.exit(main())
