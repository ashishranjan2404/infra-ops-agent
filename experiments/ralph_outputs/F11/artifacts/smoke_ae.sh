#!/usr/bin/env bash
# F11 — Offline Artifact-Evaluation smoke test (earns the "Functional" badge).
# Credential-free, deterministic. Exits 0 only if every Tier-A check passes.
set -euo pipefail

# Resolve repo root: env override, else four levels up from this script
# (experiments/ralph_outputs/F11/artifacts/smoke_ae.sh -> repo root).
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REX_REPO="${REX_REPO:-$(cd "$SCRIPT_DIR/../../../.." && pwd)}"
cd "$REX_REPO"
echo "[smoke] repo root: $REX_REPO"

echo "[smoke] 1/4 python version"
python3 --version

echo "[smoke] 2/4 benchmark registry loads"
python3 - <<'PY'
from rex.harness import scenarios_by_family
fam = scenarios_by_family()
counts = {k: len(v) for k, v in fam.items()}
print("  families:", counts)
assert all(counts.get(f, 0) > 0 for f in ("simple", "cascade", "novel")), counts
PY

echo "[smoke] 3/4 reward floor does not leak (full registry)"
python3 - <<'PY'
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "experiments"))
from rex.harness import scenarios_by_family
from rex.eval_pass_at_k import floor_check
flat = [n for names in scenarios_by_family().values() for n in names]
fc = floor_check(flat)
print("  floor_check:", fc)
assert fc["floor_ok"], "REWARD LEAK: cheapest path scored >= threshold"
PY

echo "[smoke] 4/4 deterministic judge unit tests"
python3 -m pytest tests/test_rex_deterministic_judge.py -q

echo "[smoke] PASS — Functional badge checks satisfied (offline, no credentials)."
