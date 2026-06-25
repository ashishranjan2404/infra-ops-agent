# E4 — SUMMARY

**Task:** Run Fireball-trained vs OpenSRE-trained on 8 simple incidents — does it hurt?

## Outcome: COMPLETED deliverable, BLOCKED science
The two *trained* policies do not exist in this repo (no FIREBALL corpus/slug — see
`experiments/results/P7_fireball_status.md`; the OpenSRE-GRPO Qwen was never pushed).
So the trained-vs-trained finding cannot be produced without fabrication. Per the
brief I delivered the real **comparison harness** on the 8 simple incidents, ran it
end-to-end with available frozen models as labelled STAND-INs, and documented the
Fireball blocker. Nothing fabricated; no shared core file edited.

## Artifacts
- `artifacts/compare_simple8.py` — "does it hurt?" driver for the 8 simple incidents;
  given two roster slugs, reports per-incident pass@1, delta(B−A), a `hurts` flag, an
  overall verdict, Wilson CIs, and an in-band caveat. Imports frozen REx primitives +
  the P0 deterministic judge; edits no core file.
- `artifacts/test_compare_simple8.py` — 6 offline tests (all pass).
- `run_standin.json` — real run (glm-5p2 vs minimax-m3, 3 seeds, 0 errors).
- `01..10` step docs.

## Real numbers (STAND-IN models — NOT the trained policies)
glm-5p2 (A) vs minimax-m3 (B), 8 simple incidents, seeds=3, deterministic judge:
overall pass@1 A=0.500 B=0.167; mean delta -0.333; B "hurts" on 5/8. This demonstrates
the instrument only; it says nothing about Fireball or OpenSRE transfer.

## To un-block (one command once slugs land)
    python3 artifacts/compare_simple8.py --model-a <fireball> --label-a fireball \
      --model-b <opensre> --label-b opensre --seeds 8 --out run_real.json

Needs: the FIREBALL training corpus + fireball slug, and Wenji's OpenSRE-GRPO Qwen
slug, both registered in agent/models.py ROSTER.
