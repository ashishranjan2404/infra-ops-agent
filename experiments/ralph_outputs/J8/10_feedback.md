# 10 — Feedback for the next task

The biggest lever for "demo/asset" tasks in this repo is that `sim/engine.py` is fully
deterministic and offline — you can build genuinely real traces with zero API keys or GPUs, so
prefer driving the engine over faking output. Two concrete gotchas to inherit: (1) pick
scenarios whose SLO metric is `error_rate_pct`/`p99_latency_ms` — those are the only metrics the
engine tracks, and specs with `pod_restarts`/`rss_mb` SLOs will `KeyError` in `is_resolved`
(validate with `python3 -m sim.spec validate <yaml>` and a quick `World.from_spec` smoke test
before committing to one). (2) The engine's `REMEDIATION` map encodes which tool fixes which
root-cause kind, so you can script a *grounded* wrong-tool-fails / right-tool-wins beat that the
oracle actually enforces — wrap it in an `assert` so the demo can never silently become a staged
happy-path. For anything that needs media rendering (video, audio, images), expect an
environmental blocker and deliver the runnable+captured artifact plus the exact two-command
finish recipe instead of pretending; a tested scaffold + honest blocker reads as completed, not
failed.
