# 05 — Ouroboros (3 engineers critique the spec in sequence)

## Engineer A — "the gaps engineer"
- **Problem (path fragility):** `demo_trace.py` lives 4 levels deep
  (`experiments/ralph_outputs/J8/artifacts/`). A hardcoded relative scenario path breaks when
  run from the repo root. **Fix:** compute `_REPO` via `os.path.join(__file__, ...×4)` and
  resolve non-absolute `--scenario` against it. (Applied in impl.)
- **Problem (SLO metric mismatch):** spec didn't say WHICH scenarios are safe. Some CIDG specs
  use `pod_restarts`/`rss_mb` SLOs the engine doesn't track → `is_resolved` KeyErrors.
  **Fix:** spec now pins `error_rate_pct` scenarios; default `44-search-cpu-starve` verified.

## Engineer B — "the ambiguity / over-engineering engineer"
- **Problem (color in transcript):** ANSI codes in the saved `.txt` make it ugly and break
  diffing. **Fix:** `record_demo.sh` sets `NO_COLOR=1`; `_c()` no-ops under NO_COLOR.
- **Over-engineering check:** Do we need a CLI `--scenario` at all? Yes — it lets the recorder
  swap scenarios for variants without code edits, cheap to keep. Keep.
- **Problem (silent staging):** if someone changes the band-aid tool to a correct one, the demo
  would falsely "resolve" at step 2 and the narrative collapses silently. **Fix:** `assert not
  ok` after the band-aid step makes that a hard crash, not a quiet lie.

## Engineer C — "the untested-edge engineer"
- **Edge (no asciinema):** common on fresh machines / CI. Spec already degrades, but is the exit
  code preserved when piping through `tee`? **Fix:** use `${PIPESTATUS[0]}`. (Applied.)
- **Edge (engine API drift):** if `is_resolved`/`apply_action` signatures change, the demo
  should fail loudly in tests, not in front of an audience. **Fix:** add a pytest
  (`test_demo_trace.py`) asserting T1–T5 so CI catches drift before recording.
- **Edge (cwd):** running `./record_demo.sh` from elsewhere. **Fix:** script `cd`s to its own
  dir; python resolves repo root independently.

## Final filtered spec (deltas folded in)
1. Robust `_REPO` resolution + absolute scenario path.
2. Pin `error_rate_pct` scenarios; default verified.
3. `NO_COLOR` clean transcript; `assert not ok` staging guard.
4. `PIPESTATUS` exit-code propagation; asciinema optional.
5. Add `test_demo_trace.py` (T1–T5) under artifacts/ — runnable with pytest, no network.
