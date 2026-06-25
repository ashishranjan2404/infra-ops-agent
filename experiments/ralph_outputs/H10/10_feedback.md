# 10 — Feedback for the next task

The cheapest way to make a "wrapper" deliverable trustworthy is to verify
against the *real* entrypoints before writing a line: I grepped each script's
`argparse` and read its docstring so every flag in the Makefile is provably real,
not invented — that single audit prevented the most common failure mode of glue
code (drift from the thing it wraps). Two facts worth carrying forward for this
repo: (1) `python3 -m rex.*` only resolves from the repo root, so any wrapper
must `cd $(REPO)` first; (2) HUD/gateway and training targets cannot run for free
(need `HUD_API_KEY`, `.venv-hud` py3.12, and a hand-forked Qwen slug), so the
honest validation ceiling for those is dry-run + flag-proof, while truly cheap
checks (`pytest tests`, `build_incidents.py --validate`) should be executed for
real to anchor the artifact. Prefer self-locating, override-able config
(`REPO ?=`) over hard-coded paths so the artifact survives being copied.
