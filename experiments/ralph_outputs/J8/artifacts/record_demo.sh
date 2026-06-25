#!/usr/bin/env bash
# SRE-Degrees demo recorder.
# - If asciinema is installed: records a real .cast you can publish / embed.
# - Always: captures a plain-text transcript (demo_output.txt) by running the
#   trace in --fast mode so the capture is deterministic and CI-friendly.
#
# Usage:  ./record_demo.sh
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

OUT_TXT="$HERE/demo_output.txt"
CAST="$HERE/demo.cast"

echo "[record_demo] python3: $(command -v python3)"
echo "[record_demo] capturing plain-text transcript -> $OUT_TXT"
# NO_COLOR so the saved transcript is clean ASCII; --fast for determinism.
NO_COLOR=1 python3 demo_trace.py --fast | tee "$OUT_TXT"
rc="${PIPESTATUS[0]}"
echo "[record_demo] trace exit code: $rc"

if command -v asciinema >/dev/null 2>&1; then
  echo "[record_demo] asciinema found — recording animated cast -> $CAST"
  asciinema rec --overwrite -c "python3 '$HERE/demo_trace.py'" "$CAST" || \
    echo "[record_demo] asciinema rec failed (non-fatal); transcript still produced"
else
  echo "[record_demo] asciinema NOT installed — skipping .cast (transcript is the fallback)."
  echo "[record_demo] install with:  brew install asciinema   (or pipx install asciinema)"
fi

echo "[record_demo] done. Artifacts: $OUT_TXT $( [ -f "$CAST" ] && echo "$CAST" )"
exit "$rc"
