# I4 — Improved plan (post-grill)

## What changed vs 01_plan.md
1. **Headline metric is "fraction of H(y) removed", not "H(y|R123)=0".** Accepted PSRE+SMR:
   chasing exactly-0 reproduces C12's overclaim. The witness reports `(H(y)−H(y|R123))/H(y)`.
2. **Universe split by Φ.** Entropy computed on the Φ-expressible region; the 35 topology-trap
   positives that escape Φ are reported as a *named out-of-scope residual*, not folded in.
3. **`I(y;R4|R123)` is computed and labeled Φ-bounded** via the full-feature-vector upper bound
   (data-processing inequality). Accepted RLE+AAAI.
4. **Coverage of should-block mass reported alongside entropy.** Accepted DVO — it's the
   false-allow-relevant quantity that symmetric entropy misses.
5. **PASS criterion redefined**: `>=95% of H(y) removed by 3 rules` AND
   `I(y;R4|R123) < 0.05 bits`. Honest, falsifiable, not rigged to 1.0.

## Critiques accepted
- AAAI "no number = vibe" → the whole deliverable is now the *measured* decomposition.
- AAAI "realized ≠ bound" → explicit A5; no PAC claim.
- PSRE "residual is structural" → split Φ / out-of-scope; locate residual via collisions.
- RLE "full-vector bound" → implemented as `H(y|R123) − H(y|full_Φ)`.
- DVO "entropy is symmetric" → coverage-of-block-mass added.

## Critiques rejected (with reason)
- A suggestion (implicit in SMR R1) to **target H(y|R123)=0** — REJECTED: the data shows
  0.043 bits residual from a real feature collision (rollback-without-deploy on
  cascade incidents where the rollback IS the trap). Forcing 0 would require hiding the
  collision. Honesty wins.
- Reweighting the entropy by false-allow cost (a tempting DVO extension) — REJECTED for the
  *entropy* number: a cost-weighted "entropy" is no longer Shannon entropy and breaks the
  data-processing argument. Instead the cost asymmetry is handled by the *separate* coverage
  metric, leaving the IT quantities clean.

## Deliverables (unchanged in shape, sharpened in content)
- `artifacts/entropy_witness.py` — entropy decomposition + coverage + Φ-bounded MI.
- `artifacts/three_rules_information_argument.md` — argument grounded in the printed numbers,
  cross-referencing C12's Lemma 1 (the mechanism-level proof) so the two artifacts compose:
  C12 proves *3 mechanisms*; I4 measures *how many bits each rule removes* and shows the 3rd
  rule reaches the Φ floor up to a quantified collision residual.
