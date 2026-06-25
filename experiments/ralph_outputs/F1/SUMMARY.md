# F1 — Summary: Full Related Work section

**Task:** Write the complete Related Work section (§2) for the SRE-Degrees paper, adding
real, correctly-positioned citations (CWM, AutoHarness, REx, SREGym, Constitutional AI,
RLVR/GRPO) grounded in `PAPER_OUTLINE.md` and the repo.

## Deliverables
- `artifacts/related_work.md` — full §2, ~1,930 words, 7 subsections + intro + summary
  table. Covers SREGym/AIOpsLab/ITBench, Code-as-Policies/CWM, AutoHarness harness
  synthesis, REx/Reflexion/Self-Refine, FIREBALL transfer, GRPO/RLVR/Constitutional
  AI/LLM-as-a-Judge, and pass@k/Wilson/McNemar — each positioned vs the paper's three
  claims (C1 harness, C2 transfer, C3 SME-feedback RLVR).
- `artifacts/check_related_work.py` — stdlib validator (19-token coverage + structure).

## Validation
- Validator: **PASS** — 19/19 citations, 7 subsections, table present, brackets balanced.
- `py_compile`: OK.
- No shared core files edited (rex/sim/agent diffs are pre-existing session-start state).

## Grounding
Each positioning is traced to source: AutoHarness <- `rex/harness_synth.py`; REx <-
`rex/tree.py`; deterministic-reward-vs-LLM-judge <- `rex/scoring.py`; SREGym arXiv id <-
`PAPER_QUESTIONS.md S6`.

## Honest caveat
Coverage/structure are machine-verified; *citation accuracy* (exact author/venue/DOI for
recent works CWM/SREGym/FIREBALL, and the exact REx/AutoHarness provenance) is the
residual risk and needs a camera-ready web-verification pass + a `references.bib`. See
09_critique.md.

**Status: completed.**
