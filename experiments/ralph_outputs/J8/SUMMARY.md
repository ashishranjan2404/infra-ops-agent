# J8 — Demo Video for Paper / Presentation — SUMMARY

## Task
Deliver everything needed for an SRE-Degrees demo video, given this worker cannot record video:
a storyboard/shot-list, a runnable terminal demo that drives a real end-to-end agent/sim trace,
a narration script, captured real output, and documentation of the video-recording blocker.
No shared core files edited.

## Delivered (all under experiments/ralph_outputs/J8/)
- artifacts/demo_trace.py — asciinema-style typed terminal demo. Drives the REAL deterministic
  simulator (sim/engine.py) on a real CIDG scenario (44-search-cpu-starve): incident opens at
  70% error, a tempting restart_pod band-aid fails per the engine's physics, the causal
  scale_deployment fix clears the root and SLOs go green. Exits 0 iff resolved. Offline, no key.
- artifacts/record_demo.sh — recorder: always captures a clean text transcript; records an
  animated asciinema .cast if asciinema is installed (it is not here — the blocker).
- artifacts/test_demo_trace.py — 4 pytest cases guarding the engine invariants. All pass.
- artifacts/storyboard.md — 9-shot storyboard, timecodes, capture recipe, scenario rationale.
- artifacts/narration.md — N1–N9 narration timed to the storyboard (~90s cut).
- artifacts/demo_output.txt — REAL captured transcript from running the demo.
- 01..10 step files documenting plan -> grill -> spec -> ouroboros -> impl -> tests -> critique.

## Verification
- pytest test_demo_trace.py -> 4 passed. Demo exits 0, transcript on disk. Scenario YAML
  validates via python3 -m sim.spec validate. Metrics are engine-computed, not literals.

## Blocker (honest)
The encoded video file is NOT produced — this environment cannot record/encode video, and
asciinema is not installed. The handoff to finish is two commands (in storyboard.md / 09):
asciinema rec demo.cast -c "python3 demo_trace.py" then agg demo.cast demo.gif.

## Status: completed (deliverable real; only the downstream video render is environmentally blocked).
