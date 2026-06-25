#!/usr/bin/env python3
"""verify_grpo_push.py — read-only GATE-1 verifier for E1 (Wenji's GRPO branch push).

Purpose
-------
This script does NOT run training and does NOT prove Claim 2. It verifies that Wenji's
GRPO branch, once pushed/merged, carries the *minimal sufficient* payload to replicate
"Fireball transfer beats OpenSRE on cascades", and that it is mergeable (no secrets, no
fat binaries committed raw). The science (cascade pass@1 rerun) is GATE-2, owned by us.

Exit codes (documented for the Ralph harness):
  0  GATE-1 PASS    — required payload present, parseable, no secrets.
  2  BLOCKED        — branch / payload not present yet (this is the EXPECTED state today;
                      it is a legitimate blocked status, NOT a crash).
  1  ERROR          — internal failure of the verifier itself.

Usage:
  python3 verify_grpo_push.py [--repo-root /Users/mei/rl] [--manifest E1_MANIFEST.json]

Design notes (from 05_ouroboros.md):
  * Filename-agnostic: prefers an explicit `E1_MANIFEST.json` Wenji drops in; falls back to
    content/role globs only as a hint.
  * Excludes the PRE-EXISTING in-repo inventory so our own train_rft*/run logs don't
    false-positive as "the new branch".
  * size_scan is WARN-ONLY (never flips the gate).
  * Parity reference is the v2 / deterministic path (rex/scoring.py, hud_env_v2.py).
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

# Pre-existing in-repo GRPO assets as of E1 snapshot (HEAD 8a12b41). New-branch detection
# excludes these so we don't mistake our own machinery for Wenji's push.
PREEXISTING = {
    "opensre-traj/train_rft.py",
    "opensre-traj/train_rft_v2.py",
    "opensre-traj/hud_env_static.py",
    "opensre-traj/hud_env_v2.py",
    "opensre-traj/runs/train_qwen3-8b.jsonl",
    "opensre-traj/runs/train_qwen3-8b_v2.jsonl",
    "opensre-traj/runs/train_qwen3-30b.jsonl",
}

SECRET_PATTERNS = [
    re.compile(r"HUD_API_KEY\s*[=:]\s*\S"),
    re.compile(r"\bsk-[A-Za-z0-9]{16,}"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
]
# Narrow on purpose: the Fireball SOURCE corpus, not the opensre TARGET-domain trajectories
# (opensre-traj/out/*trajectories.jsonl are the target domain and must NOT count — see
# experiments/results/P7_fireball_status.md). Generic "trajectory" globs over-match.
CORPUS_HINTS = re.compile(r"(fireball|\bdnd\b|d&d|incidents\.jsonl)", re.I)
# Paths that look corpus-ish but are the pre-existing target domain / status docs, not Wenji's push.
CORPUS_EXCLUDE = re.compile(r"(opensre-traj/out/|P7_fireball_status|ralph_outputs/)", re.I)
SIZE_WARN_BYTES = 25 * 1024 * 1024


def _check(name, ok, detail):
    return {"check": name, "ok": bool(ok), "detail": detail}


def load_manifest(repo_root, manifest_name):
    for cand in (
        os.path.join(repo_root, manifest_name),
        os.path.join(repo_root, "opensre-traj", manifest_name),
        os.path.join(os.path.dirname(__file__), manifest_name),
    ):
        if os.path.isfile(cand):
            try:
                with open(cand) as f:
                    return json.load(f), cand
            except Exception as e:  # noqa: BLE001
                return {"_parse_error": str(e)}, cand
    return None, None


def scan_corpus(repo_root):
    hits = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        if ".git" in dirpath or "ralph_outputs" in dirpath:
            dirnames[:] = [d for d in dirnames if d not in (".git",)]
            continue
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), repo_root)
            if rel in PREEXISTING:
                continue
            if CORPUS_HINTS.search(fn) and not CORPUS_EXCLUDE.search(rel):
                full = os.path.join(dirpath, fn)
                try:
                    sz = os.path.getsize(full)
                except OSError:
                    sz = 0
                hits.append((rel, sz))
    return hits


def secret_scan(paths, repo_root):
    leaks = []
    for rel in paths:
        full = os.path.join(repo_root, rel)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, "r", errors="ignore") as f:
                head = f.read(200_000)
        except OSError:
            continue
        for pat in SECRET_PATTERNS:
            if pat.search(head):
                leaks.append((rel, pat.pattern))
    return leaks


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..")))
    ap.add_argument("--manifest", default="E1_MANIFEST.json")
    args = ap.parse_args()
    repo_root = os.path.abspath(args.repo_root)

    results = []
    manifest, mpath = load_manifest(repo_root, args.manifest)

    # check 1: explicit manifest present (preferred signal of a real push)
    results.append(_check(
        "manifest_present", manifest is not None and "_parse_error" not in (manifest or {}),
        f"found at {mpath}" if manifest else f"no {args.manifest} dropped in repo (expected once Wenji pushes)"))

    # check 2: corpus present (content-hint scan, excluding pre-existing)
    corpus = scan_corpus(repo_root)
    corpus_real = [(p, s) for (p, s) in corpus if s > 0]
    results.append(_check(
        "fireball_corpus_present", bool(corpus_real),
        f"candidates: {[p for p, _ in corpus_real]}" if corpus_real
        else "no non-empty fireball/incidents/D&D trajectory corpus found"))

    # check 3: parity payload — trajectories OR grader (declared in manifest)
    parity_ok = False
    parity_detail = "manifest must declare parity_payload = trajectories|grader"
    if isinstance(manifest, dict):
        pp = manifest.get("parity_payload")
        if pp in ("trajectories", "grader") and manifest.get("parity_path"):
            ptarget = os.path.join(repo_root, manifest["parity_path"])
            parity_ok = os.path.exists(ptarget)
            parity_detail = f"parity_payload={pp} at {manifest['parity_path']} (exists={parity_ok})"
    results.append(_check("parity_payload_present", parity_ok, parity_detail))

    # check 4: model provenance
    prov_ok = bool(isinstance(manifest, dict) and manifest.get("base_model")
                   and (manifest.get("fireball_slug") or manifest.get("checkpoint_pointer")))
    results.append(_check(
        "model_provenance_present", prov_ok,
        "needs base_model + (fireball_slug | checkpoint_pointer)" if not prov_ok
        else f"base={manifest.get('base_model')} slug={manifest.get('fireball_slug')}"))

    # check 5: secret scan (WARN+GATE: secrets block the merge)
    scan_paths = [p for p, _ in corpus_real]
    if isinstance(manifest, dict):
        for k in ("parity_path", "grpo_driver", "run_log"):
            if manifest.get(k):
                scan_paths.append(manifest[k])
    leaks = secret_scan(set(scan_paths), repo_root)
    results.append(_check("no_secrets", not leaks,
                          "clean" if not leaks else f"LEAKS: {leaks}"))

    # check 6: size scan (WARN-ONLY — never flips the gate)
    big = [(p, s) for (p, s) in corpus_real if s > SIZE_WARN_BYTES]
    size_warn = f"WARN large raw files (use Git LFS/pointer): {big}" if big else "ok"

    # gate-1 verdict: load-bearing checks = corpus + parity + provenance + no_secrets
    load_bearing = {"fireball_corpus_present", "parity_payload_present",
                    "model_provenance_present", "no_secrets"}
    gate1 = all(r["ok"] for r in results if r["check"] in load_bearing)

    # ---- report ----
    print("=" * 70)
    print("E1 GATE-1 VERIFIER — Wenji GRPO branch push")
    print(f"repo_root = {repo_root}")
    print("=" * 70)
    for r in results:
        print(f"  [{'PASS' if r['ok'] else 'MISS'}] {r['check']:<28} {r['detail']}")
    print(f"  [WARN] {'size_scan':<28} {size_warn}")
    print("-" * 70)
    if gate1:
        print("GATE-1: PASS — branch payload is complete & mergeable.")
        print("NEXT (GATE-2, owned by us): re-grade Wenji's trajectories with the in-repo")
        print("  deterministic judge and run the cascade eval:")
        print("    python3 -m rex.eval_pass_at_k   # 3 policies, pass@1 by incident family")
        print("  parity assert: |our_reward - her_reward| < 1e-3 per rollout (rex/scoring.py).")
        return 0
    print("GATE-1: BLOCKED — Wenji's GRPO branch is NOT yet pushed with a complete payload.")
    print("This is the EXPECTED state today. Send artifacts/request_message_to_wenji.md.")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:  # noqa: BLE001
        print(f"verifier internal error: {e}", file=sys.stderr)
        sys.exit(1)
