# 01 — Plan (J8: Demo video for paper / presentation)

## Objective
Deliver everything needed to produce a demo video for the SRE-Degrees paper/talk,
given that this worker cannot literally record video. Concretely:
1. A **shot-list / storyboard** mapping each beat to terminal frames + narration cues.
2. A **runnable terminal demo** (real `.py` + `.sh`) that drives an actual end-to-end
   agent/sim trace and produces the on-screen output — not a mockup.
3. A **narration script** timed to the storyboard.
4. **Real captured output** from running the demo.
5. A documented **video-recording blocker**.

## Approach
Drive the REAL deterministic simulator (`sim/engine.py`) on a REAL CIDG scenario.
Use a fixed, scripted agent trajectory (diagnose → wrong band-aid → feedback →
causal fix) so the demo is byte-for-byte reproducible for a screen recording, while
every metric transition is computed by the engine's physics (no faked numbers).

Why scripted policy, not a live LLM: the brief warns against fabricated numbers and
external-API dependence; a deterministic scripted trajectory over a real engine is
honest (the resolve/non-resolve is the engine's, not ours) AND reproducible for video.

## Files to create (all task-namespaced, no shared edits)
- `artifacts/demo_trace.py` — asciinema-style typed playback driving the sim.
- `artifacts/record_demo.sh` — recorder: asciinema cast if available + text transcript.
- `artifacts/storyboard.md` — shot list / storyboard.
- `artifacts/narration.md` — timed narration.
- `artifacts/demo_output.txt` — captured real transcript.
- `01..10` + `SUMMARY.md` + `result.json`.

## Dependencies
- `sim/engine.py`, `sim/spec.py`, `scenarios/cidg/generated/*.yaml` (read-only).
- Python 3.13 stdlib + pyyaml (already in repo). NO network, NO LLM key, NO GPU.
- Optional: `asciinema` for the animated cast (NOT installed — this is the blocker).

## Risks
- Scenario SLO uses a metric the engine doesn't track (e.g. `pod_restarts`) → resolve
  oracle KeyErrors. Mitigation: pick a scenario with `error_rate_pct` SLO (verified).
- Reviewer says "scripted = not a real agent". Mitigation: be explicit it's a
  reproducible demo of the loop's *physics*; point to `rex/numbers.py` for the live run.

## Success criteria
- `python3 demo_trace.py` exits 0, shows wrong-tool-fails then right-tool-resolves with
  engine-computed metrics; transcript captured. Storyboard + narration align to it.
  Blocker (no video capture / no asciinema) documented honestly.
