# SRE-Degrees — Demo Video Shot List / Storyboard

**Target length:** 90 seconds (paper supplementary / talk opener).
**Format:** 1080p screen capture of a terminal, single take, no cuts inside the trace.
**Source of truth:** every terminal frame is produced by `demo_trace.py` — nothing is mocked.

| # | Time | Visual | On-screen / terminal | Narration cue (see narration.md) |
|---|------|--------|----------------------|----------------------------------|
| 1 | 0:00–0:06 | Title card (static slide) | "SRE-Degrees: code-as-policy incident response on a deterministic cascade simulator" | N1 |
| 2 | 0:06–0:14 | Terminal, prompt blinking, type `incident open --auto` | PAGE banner + red `error=70.0%` on `search-api` | N2 |
| 3 | 0:14–0:24 | `agent diagnose` output | hypothesis + category lines; callout: "root-cause kind hidden from agent" | N3 |
| 4 | 0:24–0:38 | `agent act --tool restart_pod` | metrics UNCHANGED (still red) + `[ORACLE] root still active` | N4 (the tension beat) |
| 5 | 0:38–0:40 | Zoom/highlight the `feedback -> refine` line | dim feedback text | N5 |
| 6 | 0:40–0:52 | `agent act --tool scale_deployment` | metrics flip to GREEN `error=0.0%` + `RESOLVED` | N6 (the payoff) |
| 7 | 0:52–1:02 | `incident summary` | attempts=2, fix, resolved=yes | N7 |
| 8 | 1:02–1:18 | Cut to architecture slide (ARCHITECTURE.md figure) | graph kernel + REx loop + oracle | N8 |
| 9 | 1:18–1:30 | Closing card | repo URL + "deterministic oracle, no reward hacking" | N9 |

## Capture recipe
1. Terminal: 100×30, dark theme, font ≥ 16pt for legibility in slides.
2. `cd experiments/ralph_outputs/J8/artifacts`
3. Record: `asciinema rec demo.cast -c "python3 demo_trace.py"` (typed playback is built in).
4. Export to GIF/MP4: `agg demo.cast demo.gif` (asciinema's `agg`) or play the `.cast` live in the talk.
5. Fallback if no asciinema: screen-record the live `python3 demo_trace.py` run; the script
   self-types at ~12 ms/char so it looks like a human at a keyboard.

## Why this scenario (44-search-cpu-starve)
- Real CIDG spec, standard `error_rate_pct` SLO so the engine's resolve oracle applies cleanly.
- `cpu_starve` is fixed by `scale_deployment` but NOT by `restart_pod` (see
  `sim/engine.py:REMEDIATION`), so the "band-aid fails, causal fix wins" beat is grounded
  in the simulator's physics, not narration.
