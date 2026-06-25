#!/usr/bin/env bash
# H8 — wrapper invoked by cron/launchd. Loads env, runs the nightly pass@k
# smoke, and logs. Kept tiny + idempotent so the scheduler entry is trivial.
#
# Cron/launchd run with a minimal environment, so we (a) cd into the repo,
# (b) source the user's env to pick up HUD_API_KEY, (c) call the python entry
# point. NOT installed by this task — see crontab.txt / launchd plist.
set -euo pipefail

REPO_ROOT="${REPO_ROOT:-/Users/mei/rl}"
ART_DIR="${REPO_ROOT}/experiments/ralph_outputs/H8/artifacts"
LOG_DIR="${ART_DIR}/logs"
mkdir -p "${LOG_DIR}"

# Load env (HUD_API_KEY etc.). cron/launchd give a bare environment, so we pull
# in the user's keys. A zshrc can contain zsh-only syntax or an interactive
# guard that aborts a `source` under bash, so we DON'T source it directly.
# Instead, in priority order:
#   1. a dedicated env file (NIGHTLY_ENV_FILE, default artifacts/.env) — POSIX
#   2. otherwise, grep just the `export KEY=...` lines out of ~/.zshrc and eval
#      them in a controlled way (never executes arbitrary zshrc logic).
load_env() {
  local envfile="${NIGHTLY_ENV_FILE:-${ART_DIR}/.env}"
  if [ -f "${envfile}" ]; then
    set +u; set -a
    # shellcheck disable=SC1090
    . "${envfile}" || true
    set +a; set -u
    return 0
  fi
  if [ -f "${HOME}/.zshrc" ]; then
    # Extract only simple `export NAME=value` lines; ignore everything else.
    while IFS= read -r line; do
      eval "export ${line#export }" 2>/dev/null || true
    done < <(grep -E '^[[:space:]]*export[[:space:]]+[A-Za-z_][A-Za-z0-9_]*=' "${HOME}/.zshrc" 2>/dev/null || true)
  fi
}
load_env

cd "${REPO_ROOT}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"

# Default to a small real smoke; pass --dry-run from the scheduler for a
# no-network self-test fire. All extra args are forwarded.
python3 "${ART_DIR}/nightly_eval.py" "$@" \
  >> "${LOG_DIR}/nightly_${STAMP}.log" 2>&1
