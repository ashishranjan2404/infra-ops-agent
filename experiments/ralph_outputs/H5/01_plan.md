# H5 — 01 Plan

## Objective
Build a real, self-contained HTML dashboard for live experiment monitoring — the
**promotion-engine dashboard**. It reads a results JSON manifest and shows
model/condition `pass@k` with a **promotion-gate** view (PROMOTE / HOLD / REJECT).
Generate a sample manifest from real A1/A2 numbers and verify the HTML loads it.

## Approach
1. A standalone schema (`sre-degrees.promotion-manifest/v1`) that is the contract
   between a generator and the HTML — not coupled to any core code.
2. `gen_manifest.py` reads two REAL, already-produced artifacts:
   - A1 `summary_table.json` (model `glm-5p2`, 630 episodes).
   - A2 `ablation_pass_at_k_deepseek-v4-pro.json` (750 episodes).
   It normalizes both into one manifest of (model, condition) candidates, each with
   `pass@1/2/5`, 95% CI, lift over its own zero_shot baseline, per-family breakdown,
   and a precomputed gate decision.
3. `dashboard.html` — pure HTML/CSS/vanilla-JS, no deps. Fetches the manifest, shows
   summary counters, a per-model table with pass@1 bar + CI band + threshold tick,
   per-family pass@1, and the gate tag with reasons. Supports drag-in of other
   manifests via a file picker (for `file://` use) and a reload button.

## Files to create (all task-namespaced, no shared edits)
- `experiments/ralph_outputs/H5/artifacts/gen_manifest.py`
- `experiments/ralph_outputs/H5/artifacts/sample_manifest.json`
- `experiments/ralph_outputs/H5/artifacts/dashboard.html`
- the 10 step docs + SUMMARY.md + result.json

## Dependencies
- Python 3 stdlib only (json, datetime). No network.
- Browser for visual; verification done headless via Node DOM shim + http.server.

## Risks
- `file://` fetch is blocked by browsers (CORS) → mitigate with a file-picker fallback
  and document `python3 -m http.server`.
- Source schemas differ (A1 uses `p1`/`ci`; A2 uses `pass@1`/`ci95`) → normalize in two
  loaders.
- Must NOT edit `experiments/dashboard.html` or any core file → everything lives under H5.

## Success criteria
- Manifest is valid JSON, schema-stamped, built from real numbers (no fabrication).
- HTML parses, fetches the manifest over HTTP (200), and renders correct gate counts.
- Gate logic is sane: only conditions that truly clear the bar (REx) get PROMOTE.
