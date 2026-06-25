# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Hard invariant in code** (from PSRE): the band-aid step asserts `not is_resolved(world)`
   so a future edit can't silently turn the demo into a staged happy-path. The wrong-tool
   failure is enforced by the engine, not by narration.
2. **Determinism is explicit** (from RLE): scripted trajectory, `--fast` flag and `DEMO_FAST`
   env to disable typing for CI/byte-stable capture; `NO_COLOR` for clean ASCII transcript.
3. **Honest disclosure, no watermark** (SMR/REV compromise): the "reproducible scripted demo
   over a real simulator" statement lives in the docstring, storyboard, and narration N-cues —
   not as an on-screen banner over the metrics.
4. **No asciinema in the hot path** (DVO): `record_demo.sh` always emits `demo_output.txt`;
   `.cast` is best-effort and clearly skipped-with-instructions if asciinema is absent.
5. **Blocker section promoted**: 07 and 09 explicitly document that video capture/encoding is
   not possible in this environment, with the exact human/CI finish commands.

## Critiques accepted
- PSRE: keep + enforce the failing attempt. **Accepted** (assert).
- RLE: no live LLM in the demo. **Accepted** (scripted policy).
- DVO: must run with bare `python3`, transcript fallback. **Accepted**.
- REV: disclose scripting. **Accepted** (in docs/narration).

## Critiques rejected (with reason)
- REV's "stamp SCRIPTED on screen as a watermark": **Rejected** — it harms the talk opener and
  the disclosure is already unambiguous in narration + docstring; a talk audience is told
  verbally. We keep the disclosure but not as a defacing overlay.
- SMR's "the video isn't a contribution so keep it light": **Partially rejected** — for this
  systems artifact the demo IS evidence it runs, so we hold the bar that every frame is
  engine-produced rather than treating it as throwaway marketing.

## Unchanged
Scenario choice (`44-search-cpu-starve`), file layout, success criteria.
