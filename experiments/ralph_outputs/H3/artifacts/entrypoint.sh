#!/usr/bin/env bash
# Entrypoint for the REx eval image. Dispatches a small, explicit set of
# subcommands so the same image serves CI smokes and real eval runs.
#
#   smoke                 -> offline, no-key health check (default CMD)
#   eval   [args...]      -> live pass@k eval (python -m rex.eval_pass_at_k)
#   shell  / bash         -> interactive shell for debugging
#   <anything else>       -> exec'd verbatim (escape hatch)
set -euo pipefail

cmd="${1:-smoke}"
shift || true

case "$cmd" in
  smoke)
    exec python3 /usr/local/bin/smoke_eval.py
    ;;
  eval)
    # Live eval needs a gateway key; warn (don't hard-fail) so the run's own
    # error surfaces if the user genuinely intended an offline-capable model.
    if [ -z "${HUD_API_KEY:-}" ] && [ -z "${ANTHROPIC_API_KEY:-}" ] \
       && [ -z "${FIREWORKS_API_KEY:-}" ]; then
      echo "[entrypoint] WARNING: no model API key set (HUD/ANTHROPIC/FIREWORKS_API_KEY)." >&2
      echo "[entrypoint] Pass one with: docker run -e HUD_API_KEY=... rex-eval eval ..." >&2
    fi
    exec python3 -m rex.eval_pass_at_k "$@"
    ;;
  shell|bash)
    exec /bin/bash
    ;;
  *)
    # Unknown first token: treat the whole argv as a command to exec.
    exec "$cmd" "$@"
    ;;
esac
