# H5 — 09 Critique (honest)

## What's weak / what a reviewer attacks
1. **Not actually "live".** It's a manifest-reading dashboard with a manual reload button,
   not a streaming monitor. There is no auto-poll/websocket and no integration with a
   running experiment loop. "Live experiment monitoring" is satisfied only in the sense
   that you regenerate the manifest and click reload. An honest framing: it's a
   **promotion-decision viewer**, and live-ness is a thin reload.
2. **Only two models, one snapshot.** A1 and A2 happened to be the two completed pass@k
   runs available. The schema generalizes, but the demo isn't a time series, so trend
   monitoring (the thing dashboards are usually for) isn't shown.
3. **Gate thresholds are arbitrary-ish.** 0.80 / 0.70 / 0.20 are reasonable but not
   derived from a cost model or a power analysis. A reviewer can argue CI_lo>=0.70 with
   N=30 is either too strict or meaningless depending on the desired error rate. They're
   documented and UI-driven, but they are a judgment call.
4. **CIs are trusted, not audited.** The dashboard renders A1/A2's CI fields verbatim. If
   those upstream CIs were computed wrong, the gate inherits the error. H5 did not re-derive
   them (by design, to avoid disagreeing with the source) — but that means the gate is only
   as trustworthy as A1/A2.
5. **No browser screenshot.** Verification is headless (Node DOM shim + HTTP 200). The shim
   exercises the real render path and asserts counters, but it does not prove the visual
   layout (bar widths, CI band placement) is pixel-correct. A human glance is still needed.
6. **`file://` caveat.** Opened directly from disk, Chrome blocks the fetch; the user must
   use the file-picker or serve the folder. Mitigated with a loud message, but it's a real
   UX wart.

## What's missing
- Auto-refresh / polling; multi-snapshot history; per-incident drill-down (data exists in
  A2's `per_incident_rewards` but the UI only goes to family granularity).
- A test that asserts bar/CI geometry, not just counts.

## Net honest assessment
Solid, real, self-contained deliverable that does exactly what the gate needs and is
backed by genuine numbers. Its honesty (rejecting baselines + the no-oracle ablation) is a
strength. Its main overclaim risk is the word "live" — it's a viewer with a reload, not a
streaming monitor.
