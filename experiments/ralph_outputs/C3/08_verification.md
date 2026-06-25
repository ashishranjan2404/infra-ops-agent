# C3 — 08 Verification

## Against success criteria (01 / 03)
| Criterion | Met? | Evidence |
|---|---|---|
| Synthesis runs on **novel-only** TRAIN, emits real rule-set + metrics | ✅ | `novel_synth_result.json`; 07 T2 |
| Held-out (novel) accuracy + FA% reported vs. both baselines | ✅ | table in 07: synth 0.941/0.059 vs seed 0.500/1.0 vs human 0.956/0.088 |
| Leakage check passes (disjoint; held-out untouched in search) | ✅ | `leakage_disjoint: true`; both search closures take `train_ex` only |
| Provenance: split ⊆ A8 certified-novel, enforced in code | ✅ | 07 T4 AssertionError on contaminated id |
| Stability reported | ✅ | 07 T3: identical across 2 runs |
| No shared core file edited | ✅ | 07 T5: only `experiments/ralph_outputs/C3/` added |

## Outputs are REAL, not placeholder
- `novel_synth_result.json` is emitted by an actual `thompson_search` run driven by live
  `gpt-5.5` calls (the operator made real HTTP round-trips; the empty-string deepseek
  reply earlier confirms calls are live, and gpt-5.5 returned valid JSON rule lists).
- The numbers are computed by the shared, unmodified `confusion`/`train_score` over
  202 labeled examples derived from real cidg scenario YAML.

## Ouroboros guards verified (05)
1. **Leakage is about closure inputs**, not just id-disjointness — confirmed: `propose`
   and `evaluate` both close over `train_ex`; `held_ex` appears only after `best` frozen.
2. **Empty-seed triviality floor present** — seed row shows 0.500 acc / **1.0 FA%** on
   held-out (allows every unsafe action), so synth's 0.941/0.059 is a genuine lift.
3. **Split criterion is a-priori and does not flatter the result** — putting the leak
   incident in HELDOUT *guarantees* 2 structurally-unfixable held-out false-allows
   (`leak_restart` unexpressible). The split costs held-out accuracy; it wasn't reverse-
   engineered to inflate it.

## Headline finding (honest, narrow)
On incidents **certified novel w.r.t. the training corpus**, autonomous rule synthesis
recovers the *language-expressible* safety boundary and **transfers it to 5 held-out
novel incidents at 94.1% accuracy / 5.9% false-allow — competitive with the hand-written
human harness (95.6% / 8.8%)**, while never seeing those incidents during search. The
gap to 100% is structural (`trap_action` and `leak_restart` are not expressible in the
6-feature language), not a synthesis failure.
