# F8 — Reproducibility Checklist · SUMMARY

**Task**: AAAI/NeurIPS-style reproducibility checklist (code, data, model weights, seeds)
grounded in the real SRE-Degrees / REx repo, honestly stating available/seeded/blocked.
Status: **completed**.

## Deliverables (under experiments/ralph_outputs/F8/)
- artifacts/REPRODUCIBILITY_CHECKLIST.md — two tiers (replay=exact, generation=distribution),
  5 axes, every row tagged AVAILABLE/SEEDED/PARTIAL/BLOCKED with path:line evidence + honest note.
- artifacts/repro_manifest.json — machine-readable, 21 items, valid JSON, SHA-stamped.
- artifacts/verify_repro.py — pure-stdlib self-audit (exit 0; 16 PASS / 3 WARN) incl. empirical
  deterministic-judge stability check.
- 10 step files (01-10).

## Key findings (measured)
- Replay tier exact; generation tier not bitwise (sampled APIs) — stated explicitly.
- hud_trajectories.jsonl committed = 197 rollouts / 3 models (opus68, haiku68, kimi61) — richer
  than DATA.md → doc drift flagged.
- scenarios/cidg/generated/*.yaml (53) UNTRACKED → not reproducible on fresh clone (top fix).
  SIMPLE tier reproducible-by-code via rex/curriculum.py:77.
- Seeds: rex/tree.py:30,67, eval_pass_at_k --seeds, ablation SEEDS=3. Judge: scoring.py:79
  deterministic (replayable) vs llm/hybrid (not).
- Weights: closed=version-pinned not weight-reproducible; open RFT recipe train_rft.py present,
  checkpoint BLOCKED (HUD key + GPU; none shipped).

## Constraints honored
No shared-core files edited; scenario-commit / DATA.md-refresh documented as recommendations only.
No fabricated numbers — all results are repo facts with shown command output (07).

## Verification
All 6 success criteria met (08): valid JSON, self-audit exit 0, all 6 sections present,
manifest SHA == HEAD, every BLOCKED names its blocker.
