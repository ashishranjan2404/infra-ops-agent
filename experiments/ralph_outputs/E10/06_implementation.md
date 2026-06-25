# E10 — Implementation

## What I built
A single, standalone, submission-grade paper section:
`experiments/ralph_outputs/E10/artifacts/fireball_transfer_section.md`.

It implements the filtered spec (post-ouroboros) exactly:

- **5.x.1 Hypothesis & motivation** — narrow falsifiable empirical claim (H1, cascades) +
  the explicitly-labeled mechanistic conjecture; H1–H4 table with a stated null per
  hypothesis; MVP subset (E3, E4) called out.
- **5.x.2 Methodology** — FIREBALL SFT → GRPO on the opensre env → frozen-policy eval through
  the same pass@k harness + deterministic reward; reward weights cited from `rex/scoring.py`/
  `ARCHITECTURE.md`; **operational definition** of trap-avoidance-rate; and the **frozen-vs-
  fine-tuned reconciliation paragraph** (the critical ouroboros fix).
- **5.x.3 Experiment design** — E3–E9 as a table (ID, question, design, metric, control,
  status), mapped verbatim-in-spirit to `experiments/NEXT_100_TASKS.md` Category E. E9 control
  is **equal trajectory budget**; E5 novel set **held out by failure-family**.
- **5.x.4 Pre-registered results** — Tables T1–T3, **every data cell `PENDING`**, plus a
  pre-registered **falsification criterion** (Wilson 95% CI null).
- **5.x.5 Status & blockers** — names E1 (model not pushed) and E2 (source corpus absent),
  cites `P7_fireball_status.md` and `CLAIMS_EVIDENCE.md`, gives the run recipe and the
  fallback if E1/E2 never land.
- **5.x.6 Threats to validity** — data-volume confound, single source domain, frozen-vs-
  finetuned tension, benchmark contamination, mechanism-as-conjecture.

## Grounding (real repo objects referenced — not invented)
- `opensre-traj/SCHEMA.md` — the `state_before → action → state_after` FIREBALL-mirrored shape.
- `rex/scoring.py` — deterministic reward `0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap`.
- `rex/eval_pass_at_k.py` — pass@k engine used for evaluation.
- `opensre-traj/hud_env_v2.py` — GRPO env.
- `experiments/NEXT_100_TASKS.md` §E — the E1–E10 task definitions.
- `experiments/results/P7_fireball_status.md`, `experiments/CLAIMS_EVIDENCE.md` — the blocker.
- `ARCHITECTURE.md`, `experiments/PAPER_OUTLINE.md` (§2.3 C2 / §3.5 / §5.3) — the framing.

## What I did NOT do (by design)
- Did not fabricate any transfer result — all result cells are the literal token `PENDING`.
- Did not edit any shared core file (`rex/*`, `sim/*`, `agent/*`, `experiments/*.py`,
  `ralph_status.json`, the paper outline, or any other task's directory). The only writes are
  under `experiments/ralph_outputs/E10/`.

## Artifacts
- `experiments/ralph_outputs/E10/artifacts/fireball_transfer_section.md` (the deliverable)
- `experiments/ralph_outputs/E10/artifacts/validate_section.py` (parse + no-fabrication gate)
