# 08 — Verification against success criteria

| Deliverable (from task) | Status | Evidence |
|-------------------------|--------|----------|
| Shot-list / storyboard script | DONE | `artifacts/storyboard.md` — 9 shots, timecodes, capture recipe |
| Asciinema-style terminal demo that runs a REAL agent/sim trace end-to-end (real .sh or .py producing demo output) | DONE | `artifacts/demo_trace.py` + `artifacts/record_demo.sh`; drives `sim/engine.py` on a real CIDG scenario; exit 0 |
| Narration script | DONE | `artifacts/narration.md` — N1–N9 timed to storyboard |
| Run the demo script to capture real output | DONE | `artifacts/demo_output.txt` (real transcript); pytest T4/T5 re-verifies on demand |
| Document the actual-video-recording blocker | DONE | 07 + 09: no video capture/encode in this env; asciinema not installed; finish recipe given |
| Do NOT edit shared core files | DONE | only `experiments/ralph_outputs/J8/**` created; `git status` shows no new edits to `sim/ rex/ agent/` from this task |

## Are the outputs real, not placeholder?
- Yes. The metric numbers (70.0% → 0.0%) are computed by `sim/engine.py:propagate()` from the
  injected fault + topology, not string literals. The pytest asserts the engine actually
  refuses the band-aid and accepts the causal fix — so the on-screen story is the simulator's
  physics. If it were faked, T2/T3 would fail.
- The demo runs with bare `python3` (verified), exits 0, transcript captured to disk.
- Storyboard + narration map 1:1 to the captured frames.

## Honest gaps (full treatment in 09)
- The agent *policy* is scripted (deterministic) for reproducible re-recording — it is NOT a
  live LLM at record time. Disclosed in the docstring, storyboard, and narration. The live LLM
  loop exists separately (`rex/numbers.py`, `rex/probe.py`) and could be filmed with a key, but
  that's nondeterministic and out of scope for a re-recordable demo.
- The final video file itself is NOT produced here (environment cannot record/encode video).
