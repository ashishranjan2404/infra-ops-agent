# G8 — SUMMARY

**Task:** Write a "why we're different" one-pager for investors/partners — synthesize the
competitive analysis into the wedge, the moat, and proof points from real results. Honest and punchy.

## Deliverables
- **`artifacts/why_were_different.md`** — the one-pager (657 words, one page). Wedge = open
  graduation benchmark (grading the *mechanism* on reconstructed real cascades, model-frozen,
  one command) + trap-action safety (-0.60 for the fix that worsens the incident). Moat =
  verifiable two-tier environment + a self-learning, generalizing verifier. Proof = 4 cited
  real-run numbers. Includes an explicit honesty block (fair-control ablation + contamination
  defense) and a partner/investor ask.
- **`artifacts/proof_points.json`** — 12 auditable claims (C1-C12), each value mapped to a real
  repo source. Valid JSON.
- `01..10` step files (plan, grill, improved plan, spec, ouroboros, implementation, tests,
  verification, critique, feedback).

## Key results / numbers (all sourced)
- 19 reconstructed real post-mortems + 51 generated scenarios.
- Reward: 0.30*diag + 0.25*fix + 0.45*resolved - 0.60*trap (resolved alone = only 45%).
- Verifier generalizes: 14->3 rules, 0.90 held-out accuracy on 3 unseen incidents.
- Discriminative: haiku 0.27 vs opus 0.50 one-shot; spread 0.0/0.15/1.0.
- Honest caveat kept on page: REx raw lift mostly oracle leakage (0.25 ~= 0.24).

## Tests
All 7 validation checks pass (JSON parse, word count, section headers, both filesystem counts,
source-file existence, run-log existence, reproducibility entrypoint).

## Honest caveats
G5/G6/G7 step outputs were empty at run time (parallel workers in flight), so the competitive
frame was sourced from underlying verified repo artifacts and made auditable. No named
competitors (none in-repo); contamination admitted, not yet quantified. No shared core files edited.

**Status: completed.**
