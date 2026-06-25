#!/usr/bin/env python3
"""Root-cause accuracy as a STANDALONE metric (Task B7).

Why this exists
---------------
`rex/scoring.py` folds diagnosis into a single graded *reward*:

    score = 0.30 * diagnosis_correct + 0.25 * fix + 0.45 * resolved  (- traps)

so a model that nails the *root cause* but botches remediation, and a model that
got lucky on remediation while misdiagnosing, can land at the SAME reward. That
conflation hides the thing an SRE evaluator most wants to know in isolation:
**did the agent correctly identify the root-cause category?**

This module reports root-cause accuracy as its OWN number, decoupled from
pass/fail. It is grounded in two existing, authoritative sources of truth and
adds no new labels of its own:

  1. `rex/scoring.py` — reuses its deterministic, hermetic stemming
     (`_stems`) so category matching is phrasing-robust and identical in spirit
     to the shipped diagnosis judge (no LLM, no network).
  2. The scenario YAML `root_cause.kind` / `root_cause.location` fields, mapped
     to the 8 gold categories via `rex/harness.py:_KIND_CATEGORY`. The same
     category taxonomy is what the HUD trajectory exports already label as
     `true_category`.

The metric is a multi-class classification accuracy: classify the agent's stated
root cause into one of the gold categories from category keyword vocabularies,
then compare to the gold category. We report overall accuracy, a per-category
confusion matrix, and (because pass/fail is the thing we are decoupling from)
the marginal disagreement between root-cause-correct and incident-resolved.

Run
---
    python3 experiments/ralph_outputs/B7/artifacts/root_cause_accuracy.py \
        --traj opensre-traj/out/hud_trajectories.jsonl
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass

# --- ground in rex/scoring.py: reuse its hermetic stemmer (no LLM, no net) ----
REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
try:
    from rex.scoring import _stems  # the deterministic judge's tokenizer
except Exception:  # pragma: no cover - fallback keeps the metric self-contained
    import re

    def _stems(text: str) -> set:  # minimal mirror of rex.scoring._stems
        toks = re.split(r"[^a-z0-9]+", (text or "").lower())
        return {t for t in toks if len(t) >= 3}


# --- gold category taxonomy (mirrors rex/harness.py:_KIND_CATEGORY) -----------
# kind -> category, used to derive the gold label from a scenario YAML.
KIND_CATEGORY = {
    "mem_leak": "resource_exhaustion", "cpu_starve": "resource_exhaustion",
    "disk_fill": "resource_exhaustion", "pool_leak": "resource_exhaustion",
    "fd_exhaust": "resource_exhaustion", "thread_exhaust": "resource_exhaustion",
    "bad_revision": "bad_deploy", "bad_content": "bad_deploy",
    "config_bloat": "config_error", "cert_expire": "config_error",
    "net_delay": "network_fault", "dns_race": "network_fault",
    "node_notready": "node_failure", "cache_flush": "saturation",
    "churn_spike": "saturation", "dep_revoked": "dependency_failure",
}

# Discriminative keyword vocab per category. Stemmed at load so matching uses the
# same stems as the answer text. Tokens chosen to separate categories, not to be
# exhaustive — overlap is resolved by the highest discriminative hit count.
_CATEGORY_TERMS = {
    "resource_exhaustion": ["memory", "leak", "oom", "cpu", "disk", "exhaust",
                            "resource", "fd", "descriptor", "thread", "pool",
                            "saturated heap", "ram", "throttle"],
    "bad_deploy": ["deploy", "deployment", "rollout", "revision", "release",
                   "regression", "rollback", "version", "bad code", "commit"],
    "config_error": ["config", "configuration", "cert", "certificate", "expire",
                     "expiry", "tls", "policy", "misconfig", "setting"],
    "network_fault": ["network", "dns", "packet", "latency", "partition", "tgw",
                      "gateway", "bgp", "routing", "connectivity", "timeout net"],
    "node_failure": ["node", "notready", "kubelet", "drain", "host", "vm down",
                     "instance", "hardware"],
    "saturation": ["saturation", "cache", "flush", "churn", "traffic surge",
                   "overload", "spike", "capacity", "queue depth"],
    "dependency_failure": ["dependency", "upstream", "revoked", "third party",
                           "downstream provider", "external", "vendor", "api quota"],
}
_CATEGORY_STEMS = {c: set().union(*[_stems(t) for t in terms])
                   for c, terms in _CATEGORY_TERMS.items()}
CATEGORIES = sorted(_CATEGORY_STEMS) + ["unknown"]


def classify_root_cause(stated: str) -> str:
    """Deterministically classify a free-text root-cause statement into one gold
    category, by max discriminative keyword overlap. Ties / no signal -> 'unknown'.

    Phrasing-robust (uses rex.scoring stems). Pure: no network, no LLM."""
    toks = _stems(stated)
    if not toks:
        return "unknown"
    scores = {c: len(toks & stems) for c, stems in _CATEGORY_STEMS.items()}
    best = max(scores.values())
    if best == 0:
        return "unknown"
    winners = [c for c, v in scores.items() if v == best]
    return winners[0] if len(winners) == 1 else "unknown"


def gold_category_from_kind(kind: str) -> str:
    return KIND_CATEGORY.get(kind, "unknown")


@dataclass
class RCAResult:
    n: int
    accuracy: float
    correct: int
    confusion: dict           # gold -> {predicted -> count}
    per_category_acc: dict    # gold -> accuracy
    # decoupling evidence: how often root-cause-correct != incident-resolved
    rc_vs_resolved_disagree: float | None
    n_with_resolved: int


def _resolved_flag(rec: dict) -> bool | None:
    """Best-effort pass/fail signal from a trajectory record, to demonstrate the
    metric is genuinely SEPARATE from pass/fail. None when unavailable."""
    if "resolved" in rec:
        return bool(rec["resolved"])
    # HUD trajectory exports: treat the binary-pass reward threshold as 'resolved'.
    if "reward" in rec and isinstance(rec["reward"], (int, float)):
        return rec["reward"] >= 0.5
    return None


def evaluate(records: list[dict]) -> RCAResult:
    """records: dicts with a model 'answer' (free text) and a gold label, either
    'true_category' (HUD export) or 'root_cause_kind' (scenario-grounded)."""
    confusion: dict = defaultdict(Counter)
    correct = n = 0
    disagree = n_resolved = 0
    for rec in records:
        gold = rec.get("true_category")
        if gold is None and "root_cause_kind" in rec:
            gold = gold_category_from_kind(rec["root_cause_kind"])
        if not gold:
            continue
        stated = rec.get("answer") or rec.get("root_cause") or ""
        pred = classify_root_cause(stated)
        confusion[gold][pred] += 1
        rc_ok = (pred == gold)
        correct += int(rc_ok)
        n += 1
        res = _resolved_flag(rec)
        if res is not None:
            n_resolved += 1
            disagree += int(rc_ok != res)
    per_cat = {}
    for gold, preds in confusion.items():
        tot = sum(preds.values())
        per_cat[gold] = round(preds.get(gold, 0) / tot, 4) if tot else 0.0
    return RCAResult(
        n=n,
        accuracy=round(correct / n, 4) if n else 0.0,
        correct=correct,
        confusion={g: dict(c) for g, c in confusion.items()},
        per_category_acc=per_cat,
        rc_vs_resolved_disagree=round(disagree / n_resolved, 4) if n_resolved else None,
        n_with_resolved=n_resolved,
    )


def load_jsonl(path: str) -> list[dict]:
    out = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Standalone root-cause accuracy metric")
    ap.add_argument("--traj", default="opensre-traj/out/hud_trajectories.jsonl",
                    help="JSONL of trajectories with 'answer' + 'true_category'")
    ap.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = ap.parse_args(argv)

    path = args.traj
    if not os.path.isabs(path):
        path = os.path.join(REPO, path)
    recs = load_jsonl(path)
    res = evaluate(recs)

    if args.json:
        print(json.dumps(res.__dict__, indent=2, default=dict))
        return 0

    print(f"Root-cause accuracy (standalone): {res.accuracy:.3f}  "
          f"({res.correct}/{res.n})")
    print(f"Records evaluated: {res.n}")
    print("\nPer-category accuracy (gold -> recall):")
    for cat in sorted(res.per_category_acc):
        print(f"  {cat:22s} {res.per_category_acc[cat]:.3f}")
    print("\nConfusion (gold -> predicted counts):")
    for gold in sorted(res.confusion):
        print(f"  {gold:22s} {res.confusion[gold]}")
    if res.rc_vs_resolved_disagree is not None:
        print(f"\nDecoupling check: root-cause-correct disagrees with incident-"
              f"resolved on {res.rc_vs_resolved_disagree:.1%} of "
              f"{res.n_with_resolved} records")
        print("  (non-zero => this metric carries signal pass/fail does NOT.)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
