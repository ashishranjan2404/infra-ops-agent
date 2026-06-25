#!/usr/bin/env python3
"""Fetch the FIREBALL D&D trajectory dataset (lara-martin/FIREBALL) from the
HuggingFace Hub.

FIREBALL (Zhu et al., ACL 2023, arXiv:2305.01528) is ~25k Discord D&D combat
sessions captured via the Avrae bot. It is PUBLIC, non-gated, CC-BY-4.0, but
large: 1475 `filtered/*.jsonl` shard files, size_categories 100K<n<1M.

This script does NOT download the whole repo by default. It downloads a small
number of shards (``--shards N``) so you can validate the converter without
pulling gigabytes. Use ``--all`` for the full dataset.

Usage:
    python fireball_fetch.py --shards 1 --out data/fireball_raw
    python fireball_fetch.py --all  --out data/fireball_raw   # full download

Each shard line is one combat "turn instance" — see fireball_schema.py.
"""
from __future__ import annotations

import argparse
import socket
import sys
from pathlib import Path

REPO_ID = "lara-martin/FIREBALL"
REPO_TYPE = "dataset"


def list_shards(api) -> list[str]:
    files = api.list_repo_files(REPO_ID, repo_type=REPO_TYPE)
    return sorted(f for f in files if f.startswith("filtered/") and f.endswith(".jsonl"))


def fetch(n_shards: int | None, out: Path, timeout: int = 60) -> list[Path]:
    socket.setdefaulttimeout(timeout)
    try:
        from huggingface_hub import HfApi, hf_hub_download
    except ImportError:  # pragma: no cover - dependency guard
        sys.exit("huggingface_hub not installed: pip install huggingface_hub")

    api = HfApi()
    shards = list_shards(api)
    if not shards:
        sys.exit("No filtered/*.jsonl shards found — dataset layout changed?")
    if n_shards is not None:
        shards = shards[:n_shards]

    out.mkdir(parents=True, exist_ok=True)
    local: list[Path] = []
    for i, rel in enumerate(shards, 1):
        p = hf_hub_download(REPO_ID, rel, repo_type=REPO_TYPE)
        dst = out / Path(rel).name
        if not dst.exists():
            dst.symlink_to(p)
        local.append(dst)
        print(f"[{i}/{len(shards)}] {rel} -> {dst}", file=sys.stderr)
    return local


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--shards", type=int, default=1, help="how many shards to fetch")
    ap.add_argument("--all", action="store_true", help="fetch all 1475 shards")
    ap.add_argument("--out", type=Path, default=Path("data/fireball_raw"))
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args()
    n = None if a.all else a.shards
    paths = fetch(n, a.out, a.timeout)
    print(f"fetched {len(paths)} shard(s) into {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
