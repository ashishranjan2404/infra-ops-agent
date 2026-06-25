# F7 — 06 Implementation

## What I built (all real, all task-namespaced under F7/artifacts/)

1. **`artifacts/rebuttal_anticipation.md`** — the deliverable. 10 attacks (A1–A10), each with:
   strongest-form Steelman, best Honest response, Probability {High/Medium/Low}, Depth
   {Fatal-if-true/Serious/Manageable}, and Closing evidence. Plus two top-line callouts
   (highest-probability = small N; highest-depth = construct validity), a 4-item concession
   ledger, and a "what would actually sink the paper" section. Every attack is grounded in a
   real repo fact: the reward formula `0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap`, the
   flat RFT (`0.522 → 0.491` over 25 steps from `opensre-traj`), the `0.86 = (4×1.0+0.30)/5`
   fixed point, ~51 CIDG YAML + 19 reconstructed post-mortem specs, 5 frozen models × 5 hard
   incidents, the deterministic-judge fallback in `rex/scoring.py`, and gateway-routed models.

2. **`artifacts/attacks.json`** — machine-readable index (id, title, theme, probability, depth,
   one_line_response) for all 10 attacks. Themes cover all five dispatch-mandated weaknesses:
   `synthetic_data, small_n, flat_rft, reward_hacking, single_domain` (+ construct_validity,
   fixed_point, judge_circularity, reproducibility, generality).

3. **`artifacts/validate_attacks.py`** — stdlib-only validator (the test harness):
   - schema-checks attacks.json (8–12 attacks, n_attacks consistent, valid prob/depth enums);
   - asserts all five mandatory themes are present (`check_themes`);
   - structurally validates the markdown (`check_doc`): four required H2 sections, both top-line
     callouts, one `### A<n>` block per attack id, all five labeled lines per block (tolerant
     regex), a substance gate (Steelman + Honest-response bodies ≥120 chars), and the A6
     fixed-point arithmetic (`(4` and `0.30`) literally present.

## Coverage of the 5 mandated real weaknesses
- synthetic data → A3 (reconstruction/answer-leakage) · small N → A1 · flat RFT → A4 ·
  reward-hacking → A5 (+ A8 judge circularity) · single domain → A7. Plus A2 construct
  validity, A6 fixed point, A9 reproducibility, A10 method novelty.

## No shared core files touched
Only files under `experiments/ralph_outputs/F7/` were created. `rex/`, `sim/`, `agent/`,
`opensre-traj/`, scenario YAML, and other tasks' directories were read-only.

## Fixes applied during build (see 07)
- Label regex made punctuation-tolerant (`**Steelman.**` form).
- Substance-gate body extraction fixed to stop at the next *known label*, not any inline bold,
  so a steelman that bolds a number mid-sentence isn't truncated/false-flagged.
