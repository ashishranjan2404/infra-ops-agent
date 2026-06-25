#!/usr/bin/env bash
# H6 CI gate: every CIDG scenario YAML must pass the sim engine.
# Drop-in for a CI step. Exits nonzero (propagated) when any scenario fails.
#
#   - name: Validate scenarios
#     run: experiments/ralph_outputs/H6/artifacts/ci_check.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
cd "$REPO_ROOT"

exec python3 experiments/ralph_outputs/H6/artifacts/ci_validate_scenarios.py \
  --json experiments/ralph_outputs/H6/ci_report.json \
  "$@"
