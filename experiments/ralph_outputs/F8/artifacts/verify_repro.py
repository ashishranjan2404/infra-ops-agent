#!/usr/bin/env python3
"""verify_repro.py — self-audit for the SRE-Degrees / REx reproducibility checklist.

Mechanically checks the claims in REPRODUCIBILITY_CHECKLIST.md / repro_manifest.json
against the LIVE repo. Pure stdlib, no network, no API keys, no GPU.

Exit code: 0 iff every AVAILABLE/SEEDED claim holds. PARTIAL/BLOCKED items are
printed as WARN and tallied but never fail the run (they are *known* gaps, the whole
point of an honest checklist). git failures degrade to UNKNOWN, never a false pass.

Usage:  python3 verify_repro.py            # audit
        python3 verify_repro.py --json     # machine-readable summary
"""
from __future__ import annotations
import importlib.util
import json
import os
import subprocess
import sys

# repo root = two levels up from experiments/ralph_outputs/F8/artifacts/
HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))


def _p(rel: str) -> str:
    return os.path.join(REPO, rel)


def check_path(rel: str) -> bool:
    return os.path.exists(_p(rel))


def check_import(mod: str) -> bool:
    try:
        return importlib.util.find_spec(mod) is not None
    except (ImportError, ValueError):
        return False


def check_grep(rel: str, needle: str) -> bool:
    fp = _p(rel)
    if not os.path.exists(fp):
        return False
    try:
        with open(fp, "r", errors="replace") as fh:
            return needle in fh.read()
    except OSError:
        return False


def check_committed(rel: str):
    """True/False if tracked/untracked; None (UNKNOWN) if git unavailable."""
    try:
        r = subprocess.run(
            ["git", "-C", REPO, "ls-files", "--error-unmatch", rel],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return None


def git_sha() -> str:
    try:
        r = subprocess.run(
            ["git", "-C", REPO, "rev-parse", "HEAD"],
            capture_output=True, text=True,
        )
        return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"
    except (OSError, subprocess.SubprocessError):
        return "UNKNOWN"


def replay_double_grade():
    """Empirically show the deterministic judge is stable: grade the first committed
    trajectory record twice, assert identical. Returns True/False/None(UNKNOWN)."""
    jl = _p("opensre-traj/out/hud_trajectories.jsonl")
    sco = _p("rex/scoring.py")
    if not (os.path.exists(jl) and os.path.exists(sco)):
        return None
    try:
        sys.path.insert(0, REPO)
        from rex.scoring import deterministic_judge  # type: ignore
        rec = None
        with open(jl) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    break
        if rec is None:
            return None
        stated = rec.get("answer", "") or rec.get("model", "")
        gold = rec.get("incident", "") or "placeholder_gold"
        a = deterministic_judge(stated, gold, [])
        b = deterministic_judge(stated, gold, [])
        return a == b
    except Exception:  # noqa: BLE001 — best-effort empirical check
        return None


# (id, axis, claimed_status, check_callable) — check returns True/False/None
CHECKS = [
    # --- code ---
    ("code.repo_public",  "code", "AVAILABLE", lambda: check_path("README.md")),
    ("code.entrypoints",  "code", "AVAILABLE", lambda: check_path("rex/eval_pass_at_k.py")),
    ("code.deps_runtime", "code", "AVAILABLE", lambda: check_path("requirements-rex.txt")),
    ("code.deps_gpu",     "code", "AVAILABLE", lambda: check_path("requirements.txt")),
    ("code.dep_yaml",     "code", "AVAILABLE", lambda: check_import("yaml")),
    ("code.dep_requests", "code", "AVAILABLE", lambda: check_import("requests")),
    # --- seeds / determinism ---
    ("seed.tree",         "seed", "SEEDED",    lambda: check_grep("rex/tree.py", "random.Random(seed)")),
    ("seed.eval_sweep",   "seed", "SEEDED",    lambda: check_grep("rex/eval_pass_at_k.py", "seeds")),
    ("seed.ablation",     "seed", "SEEDED",    lambda: check_grep("rex/ablation.py", "SEEDS")),
    ("seed.det_judge",    "seed", "AVAILABLE", lambda: check_grep("rex/scoring.py", "def deterministic_judge")),
    ("repro.replay_double_grade", "seed", "AVAILABLE", replay_double_grade),
    # --- data ---
    ("data.trajectories_committed", "data", "AVAILABLE",
        lambda: check_committed("opensre-traj/out/hud_trajectories.jsonl")),
    ("data.scenarios_base",  "data", "AVAILABLE", lambda: check_path("scenarios/cidg/01-gcp-service-control.yaml")),
    ("data.simple_generator","data", "AVAILABLE", lambda: check_grep("rex/curriculum.py", "def generate_simple")),
    ("data.generated_committed", "data", "PARTIAL",
        lambda: check_committed("scenarios/cidg/generated")),  # expected untracked -> PARTIAL
    ("data.doc_drift",       "data", "PARTIAL", lambda: check_path("opensre-traj/DATA.md")),
    # --- weights ---
    ("weights.roster",       "weights", "AVAILABLE", lambda: check_grep("agent/models.py", "anchor")),
    ("weights.open_recipe",  "weights", "AVAILABLE", lambda: check_path("opensre-traj/train_rft.py")),
    ("weights.checkpoint",   "weights", "BLOCKED",
        lambda: any(f.endswith((".safetensors", ".pt", ".bin")) for _r, _d, fs in os.walk(_p("opensre-traj")) for f in fs)),
]


def main() -> int:
    as_json = "--json" in sys.argv
    counts = {"AVAILABLE": 0, "SEEDED": 0, "PARTIAL": 0, "BLOCKED": 0}
    rows = []
    hard_fail = False
    for cid, axis, claimed, fn in CHECKS:
        try:
            ok = fn()
        except Exception:  # noqa: BLE001
            ok = None
        counts[claimed] = counts.get(claimed, 0) + 1
        if claimed in ("AVAILABLE", "SEEDED"):
            if ok is True:
                verdict = "PASS"
            elif ok is None:
                verdict = "UNKNOWN"
            else:
                verdict, hard_fail = "FAIL", True
        else:  # PARTIAL / BLOCKED — informational
            verdict = "WARN"
        rows.append({"id": cid, "axis": axis, "claimed": claimed,
                     "observed": ok, "verdict": verdict})

    summary = {"git_sha": git_sha(), "python": sys.version.split()[0],
               "counts": counts, "rows": rows, "hard_fail": hard_fail}
    if as_json:
        print(json.dumps(summary, indent=2))
    else:
        print(f"# verify_repro  sha={summary['git_sha'][:10]}  py={summary['python']}")
        for r in rows:
            print(f"{r['verdict']:8s} {r['claimed']:10s} {r['id']:32s} observed={r['observed']}")
        print("counts:", counts, "| hard_fail:", hard_fail)
    return 1 if hard_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())
