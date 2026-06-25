# F4 — 08_verification

## Against 01_plan success criteria
| Criterion | Status | Evidence |
|---|---|---|
| Script runs, 0 errors, ≥5 PNGs | ✅ | T1: exit 0, 6 PNGs |
| Each PNG ≥150 DPI, non-empty | ✅ | T2: 200 DPI, 60–99 KB each, PIL-valid |
| Every number traces to a real JSON field | ✅ | T3: 5 assertions vs A1/A2/frontier/harness |
| No shared core file modified | ✅ | T4: `find -newermt` empty for shared `.py` |

## Are the outputs real (not placeholder)?
Yes. The figures are rendered from the committed result JSONs:
- A1 = 630-episode glm-5p2 run (126 ep/condition).
- A2 = 750-episode deepseek-v4-pro ablation + McNemar.
- frontier.json = 5 models × 5 scenarios.
- harness_synth_v2.json = real HUD job `abf124e23b954b258319758093ddc9f7`.
No hard-coded literals stand in for data; every plotted value is read at runtime. I visually
inspected fig1, fig4, fig6 — bar heights, CI whiskers, and annotations match the JSON.

## Honest caveats surfaced (not hidden)
- fig1–3 keep `REx (no oracle)` sitting with the baselines, faithfully showing A2's own finding
  that the lift comes from oracle feedback, not the tree.
- fig5 makes the "all models → 0.86" plateau explicit in the title rather than hiding it.
- fig6 shows the learned harness (0.897 acc / 0.308 false-allow) is *below* the hand-written
  oracle (0.949 / 0.154) — an honest gap, not an over-claim.

**Verdict: meets all success criteria with real, inspected outputs.**
