# syntax=docker/dockerfile:1
# ---------------------------------------------------------------------------
# Reproducible eval image for the REx SRE-Degrees pipeline.
#
# Grounded in requirements-rex.txt (the CPU runtime stack: pyyaml, requests,
# matplotlib, numpy). The heavy GPU/SFT stack (requirements.txt: unsloth/trl)
# is intentionally NOT installed — it is not needed to run the sim/loop/eval.
#
# Build (from repo root /Users/mei/rl):
#   docker build -f experiments/ralph_outputs/H3/artifacts/Dockerfile \
#       -t rex-eval:latest .
#
# Run an OFFLINE smoke (no API key, deterministic synthetic harness):
#   docker run --rm rex-eval:latest smoke
#
# Run the LIVE pass@k eval (needs a gateway key):
#   docker run --rm -e HUD_API_KEY="$HUD_API_KEY" rex-eval:latest \
#       eval --model glm-5p2 --per-family 2 --seeds 3
# ---------------------------------------------------------------------------

# Pin a minor version (not :latest) for reproducible rebuilds. Slim = small base.
FROM python:3.13-slim AS base

# Fail fast & loud; no .pyc churn; unbuffered logs for live container output.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# --- Dependency layer (cached independently of source) ---------------------
# Copy ONLY the requirements file first so the pip layer is reused unless the
# deps actually change. This is the single most important build-cache win.
COPY requirements-rex.txt ./requirements-rex.txt
RUN pip install --no-cache-dir -r requirements-rex.txt

# --- Source layer ----------------------------------------------------------
# Copy the packages the eval entrypoint imports. Keeping this explicit (rather
# than `COPY . .`) keeps the image small and the layer stable.
COPY agent/ ./agent/
COPY rex/ ./rex/
COPY sim/ ./sim/
COPY experiments/ ./experiments/
COPY scenarios/ ./scenarios/

# The entrypoint + offline smoke (live alongside this Dockerfile).
COPY experiments/ralph_outputs/H3/artifacts/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY experiments/ralph_outputs/H3/artifacts/smoke_eval.py /usr/local/bin/smoke_eval.py
RUN chmod +x /usr/local/bin/entrypoint.sh /usr/local/bin/smoke_eval.py

# --- Runtime hardening -----------------------------------------------------
# Run as a non-root user (least privilege; required by many CI/k8s policies).
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app
USER appuser

# PYTHONPATH so `python3 -m rex.eval_pass_at_k` resolves repo-root imports.
ENV PYTHONPATH=/app

# Default to the offline smoke so a bare `docker run` proves the image works
# without any secret. Override the subcommand to run the live eval.
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["smoke"]
