#!/usr/bin/env python3
"""D14 — assemble the 42-incident RFT task set from the opensre corpus.

The opensre incident corpus (opensre-traj/out/trajectories.jsonl) holds 319 scenario
records: 34 *canonical* incidents (15 synthetic seed classes 001-015 + 19 real
postmortem-derived incidents 101-119) plus 285 perturbed variants (suffix -sNNN).

`hud_env_v2.investigate_v2` already exposes one task per *canonical* id via
`canonical_ids()`, i.e. 34 tasks. The RFT runner (`train_rft_v2.py`) currently trains on
only the first 10 of those (`--tasks 0..9`). This script assembles a *42-incident* task
set so the whole benchmark — and a curated curriculum slice beyond the 34 canonical
incidents — can be used for RFT.

Selection (deterministic, no network):
  * all 34 canonical incidents (the full benchmark), then
  * 8 held-out *hard variants* (one -sNNN variant from 8 distinct synthetic bases) to
    reach exactly 42 and add within-class diversity the canonical set lacks.

Output: a JSON task file consumed by `train_rft_42.py` / `train_rft_42.yaml`.
Each task carries the env scenario_id + difficulty + class so a curriculum/sampler can
order them. The scenario_ids are REAL keys present in the corpus (validated here).

Usage:
    python3 assemble_tasks.py [--n 42] [--out tasks_42.json] [--corpus <path>]
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
# repo-relative corpus (opensre-traj/out/trajectories.jsonl)
DEFAULT_CORPUS = HERE.parents[3] / "opensre-traj" / "out" / "trajectories.jsonl"

_VARIANT_RE = re.compile(r"-s\d+$")


def load_corpus(corpus: Path) -> dict[str, dict]:
    recs: dict[str, dict] = {}
    with corpus.open() as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            recs[r["scenario_id"]] = r
    return recs


def _difficulty(rec: dict) -> int:
    # corpus records carry `difficulty` (3-5 in this corpus); default mid.
    d = rec.get("difficulty", rec.get("scenario_difficulty"))
    try:
        return int(d)
    except (TypeError, ValueError):
        return 3


def _category(rec: dict) -> str:
    return (rec.get("answer", {}) or {}).get("root_cause_category", "unknown")


def assemble(recs: dict[str, dict], n: int = 42) -> list[dict]:
    all_ids = sorted(recs)
    canonical = [s for s in all_ids if not _VARIANT_RE.search(s)]
    canonical.sort()
    if n < len(canonical):
        chosen = canonical[:n]
    else:
        chosen = list(canonical)
        need = n - len(chosen)
        # one hard variant per distinct synthetic base (001-015), deterministic order,
        # preferring the highest-numbered variant (the most perturbed) of each base.
        by_base: dict[str, list[str]] = {}
        for s in all_ids:
            if _VARIANT_RE.search(s):
                base = _VARIANT_RE.sub("", s)
                by_base.setdefault(base, []).append(s)
        extra: list[str] = []
        for base in sorted(by_base):
            variants = sorted(by_base[base])
            if variants:
                extra.append(variants[-1])  # most-perturbed variant of this base
            if len(extra) >= need:
                break
        chosen.extend(extra[:need])

    tasks = []
    for i, sid in enumerate(chosen):
        rec = recs[sid]
        is_canon = not _VARIANT_RE.search(sid)
        is_real = bool(re.match(r"^1\d\d-", sid))
        tasks.append({
            "index": i,
            "scenario_id": sid,
            "category": _category(rec),
            "difficulty": _difficulty(rec),
            "kind": "canonical" if is_canon else "variant",
            "origin": "real_postmortem" if is_real else "synthetic",
        })
    return tasks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=42)
    ap.add_argument("--out", default=str(HERE / "tasks_42.json"))
    ap.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    args = ap.parse_args()

    corpus = Path(args.corpus)
    if not corpus.exists():
        raise SystemExit(f"corpus not found: {corpus}")

    recs = load_corpus(corpus)
    tasks = assemble(recs, n=args.n)

    # validate: every scenario_id resolves in the corpus + ids are unique
    seen = set()
    for t in tasks:
        sid = t["scenario_id"]
        assert sid in recs, f"unknown scenario_id {sid}"
        assert sid not in seen, f"duplicate scenario_id {sid}"
        seen.add(sid)

    n_canon = sum(1 for t in tasks if t["kind"] == "canonical")
    n_real = sum(1 for t in tasks if t["origin"] == "real_postmortem")
    payload = {
        "name": "opensre-42-incident",
        "env_module": "hud_env_v2.py",
        "env_template": "investigate_v2",
        "scenario_arg": "scenario_id",
        "count": len(tasks),
        "n_canonical": n_canon,
        "n_variants": len(tasks) - n_canon,
        "n_real_postmortem": n_real,
        "n_synthetic": len(tasks) - n_real,
        "corpus": str(corpus),
        "tasks": tasks,
    }
    out = Path(args.out)
    out.write_text(json.dumps(payload, indent=2) + "\n")
    print(f"wrote {out} : {len(tasks)} tasks "
          f"({n_canon} canonical + {len(tasks) - n_canon} variants; "
          f"{n_real} real / {len(tasks) - n_real} synthetic)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
