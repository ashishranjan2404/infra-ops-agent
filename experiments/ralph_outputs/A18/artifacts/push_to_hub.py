#!/usr/bin/env python3
"""push_to_hub.py — upload the OpenSRE Incident-Diagnosis Trajectories dataset to the HF Hub.

Builds the upload package from the canonical source files, splits the JSONL into
`synthetic/` and `real/` shards (so the `synthetic`/`real` configs in the dataset card
resolve), and pushes everything with `huggingface_hub.HfApi.upload_folder`.

Auth (one of):
    export HF_TOKEN=hf_xxx            # recommended for CI
    huggingface-cli login            # interactive

Usage:
    python push_to_hub.py --repo-id <org>/opensre-incident-trajectories
    python push_to_hub.py --repo-id <org>/opensre-incident-trajectories --private
    python push_to_hub.py --repo-id <org>/opensre-incident-trajectories --dry-run

`--dry-run` stages the full package into a temp dir and validates it WITHOUT any network call —
use it to confirm the deliverable is upload-ready when no HF credentials are present.
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# Canonical source files, relative to this script's directory.
HERE = Path(__file__).resolve().parent
# When run from the repo, the real data lives here; the artifacts dir also ships a copy.
SRC_JSONL_CANDIDATES = [
    HERE / "hud_trajectories.jsonl",
    Path("/Users/mei/rl/opensre-traj/out/hud_trajectories.jsonl"),
]
README = HERE / "README.md"
LOADER = HERE / "opensre_trajectories.py"


def find_source_jsonl() -> Path:
    for c in SRC_JSONL_CANDIDATES:
        if c.exists():
            return c
    raise FileNotFoundError(f"No source jsonl found in {SRC_JSONL_CANDIDATES}")


def build_package(stage: Path) -> dict:
    """Assemble the upload folder. Returns a stats dict."""
    stage.mkdir(parents=True, exist_ok=True)
    src = find_source_jsonl()

    records = [json.loads(l) for l in src.read_text().splitlines() if l.strip()]

    # Root jsonl = the `all` config / default `train` split.
    (stage / "hud_trajectories.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n"
    )

    # Per-source shards for the `synthetic` / `real` configs.
    for source in ("synthetic", "real"):
        sub = [r for r in records if r.get("source") == source]
        d = stage / source
        d.mkdir(exist_ok=True)
        (d / f"{source}.jsonl").write_text(
            "\n".join(json.dumps(r, ensure_ascii=False) for r in sub) + "\n"
        )

    # Card + loader.
    shutil.copy(README, stage / "README.md")
    shutil.copy(LOADER, stage / "opensre_trajectories.py")

    return {
        "n_total": len(records),
        "n_synthetic": sum(r.get("source") == "synthetic" for r in records),
        "n_real": sum(r.get("source") == "real" for r in records),
        "files": sorted(p.relative_to(stage).as_posix() for p in stage.rglob("*") if p.is_file()),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-id", default="<org>/opensre-incident-trajectories")
    ap.add_argument("--private", action="store_true")
    ap.add_argument("--dry-run", action="store_true", help="Build + validate package, no upload.")
    ap.add_argument("--token", default=os.environ.get("HF_TOKEN"))
    args = ap.parse_args()

    stage = Path(tempfile.mkdtemp(prefix="opensre_hf_"))
    stats = build_package(stage)
    print(f"[build] staged package at {stage}")
    print(f"[build] total={stats['n_total']} synthetic={stats['n_synthetic']} real={stats['n_real']}")
    for f in stats["files"]:
        print(f"  - {f}")

    if args.dry_run:
        print("[dry-run] package is upload-ready; skipping network upload.")
        return 0

    if not args.token:
        print(
            "[error] no HF token. Set HF_TOKEN or run `huggingface-cli login`, "
            "or re-run with --dry-run.",
            file=sys.stderr,
        )
        return 2
    if args.repo_id.startswith("<"):
        print("[error] pass a real --repo-id (e.g. myorg/opensre-incident-trajectories).",
              file=sys.stderr)
        return 2

    from huggingface_hub import HfApi  # imported late so --dry-run needs no hub at all

    api = HfApi(token=args.token)
    api.create_repo(repo_id=args.repo_id, repo_type="dataset",
                    private=args.private, exist_ok=True)
    api.upload_folder(
        repo_id=args.repo_id,
        repo_type="dataset",
        folder_path=str(stage),
        commit_message="Add OpenSRE Incident-Diagnosis Trajectories (197 graded SRE trajectories)",
    )
    print(f"[ok] pushed to https://huggingface.co/datasets/{args.repo_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
