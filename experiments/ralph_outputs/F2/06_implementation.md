# F2 — 06 Implementation

## What I built (all task-namespaced under `F2/artifacts/`, no core edits)

1. **`artifacts/LIMITATIONS.md`** — the deliverable. A paste-ready `## Limitations`
   section with six grounded subsections (L1–L6) plus a `### Scope` closer. Every
   empirical claim carries a parenthetical source. Grounded entirely in real
   `experiments/` findings:
   - L1 synthetic data — 42 evaluated / 51 on-disk generated incidents.
   - L2 oracle circularity — generator co-authored with `rex/scoring.py` judge.
   - L3 preliminary RFT — v1 declined (0.522→0.491), v2 +0.037 over 15 steps.
   - L4 reward hacking — D13's 5 exploit classes, hedge 92.9% fool-rate, 0.30 cap.
   - L5 single-domain + BLOCKED Fireball transfer (P7).
   - L6 statistical power — indistinguishable ablation band, partial 750-ep run,
     single-model, semi-synthetic SME feedback.
   - Scope — names the two surviving results (harness 89.7%; REx-SME 2.8×).

2. **`artifacts/evidence_index.md`** — audit table mapping each anchor fact to its
   source file, all marked verified.

3. **`artifacts/check_limitations.py`** — stdlib validator: confirms every cited
   file exists, the generated-scenario glob ≥ 30, and LIMITATIONS.md has the full
   L1–L6 + Scope structure. Derives repo root dynamically (Ouroboros fix C).

## Grounding method
I read `FINAL_SUMMARY.md`, `CLAIMS_EVIDENCE.md`, and `ralph_outputs/D13/SUMMARY.md`,
and grepped `rex/scoring.py` for the reward weights (W_ROOT=0.30, W_FIX=0.25,
W_RESOLVED=0.45 — confirmed) and the generated-scenario glob (51 files — confirmed).
No number in LIMITATIONS.md is invented; each was lifted from a real artifact.

## Proposed-change note (per brief)
This task is documentation only and requires **no** edit to any shared core file.
The mitigations named in L4 (negation detection, commitment penalty, component
binding, NFKC normalization) are described as *designed, not built* — consistent
with D13, which also documents them as unbuilt. No `.patch` against core files is
needed for F2.
