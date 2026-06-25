# F8 · 08 Verification against success criteria

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| Checklist covers code/data/weights/seeds, each item tagged AVAILABLE/SEEDED/PARTIAL/BLOCKED with a real pointer | ✅ | `REPRODUCIBILITY_CHECKLIST.md` §1–5, every row has `path:line` + tag; structural parse PASS (07-C). |
| `repro_manifest.json` parses as valid JSON | ✅ | 07-B: `json.load` ok, 21 items, counts sum to 21. |
| `verify_repro.py` runs and emits pass/fail vs live repo | ✅ | 07-A: exit 0, 16 PASS / 2 WARN / 1 WARN(BLOCKED). |
| Every BLOCKED item names a concrete blocker | ✅ | `weights.checkpoint` → "needs HUD_API_KEY + GPU + forked Qwen slug, no weights shipped"; PARTIALs name untracked-data / stale-doc. |
| Grounded in ACTUAL repo layout | ✅ | Cites `rex/tree.py:30`, `rex/scoring.py:79`, `rex/curriculum.py:77`, `agent/models.py`, `opensre-traj/train_rft.py`, measured 197-rollout dataset. |
| No shared-core files edited | ✅ | All writes under `experiments/ralph_outputs/F8/`; the scenario-commit fix is documented in 06, **not applied** (`git status` of `rex/`,`sim/`,`agent/` unchanged). |

## Are the outputs real (not placeholder)?
- **verify_repro.py** actually imports `rex.scoring` and grades a real committed
  trajectory record twice — not a stub. It calls `git ls-files` and walks the tree.
- **Dataset counts (197, 3 models)** were *measured* by parsing the committed `.jsonl`,
  not copied from a doc (and indeed *contradict* the stale doc — caught and flagged).
- **Untracked-scenario gap** verified via `git status` showing `?? scenarios/cidg/generated/`.
- **Seed/judge pointers** verified by grep returning the exact lines.

## Honesty audit (did I overclaim?)
- Did **not** mark the generation tier "reproducible" — split into replay (✅ exact) vs
  generation (🎲 distribution-only), per the grill's central disagreement.
- Did **not** launder the untracked scenarios into a green — PARTIAL with the fix named.
- Did **not** claim a checkpoint exists — BLOCKED, blocker named.
- Reported the doc/data drift *against my own project's documentation* rather than
  hiding it.

Conclusion: all success criteria met; deliverable is real, self-auditing, and honest
about negatives.
