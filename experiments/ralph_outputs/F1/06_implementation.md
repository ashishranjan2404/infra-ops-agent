# 06 — Implementation

## What I built (real artifacts)
1. `artifacts/related_work.md` — the full Related Work section (§2), ~1,930 words,
   7 subsections + intro + summary table:
   - §2.1 SRE agent benchmarks/harnesses — SREGym (arXiv:2605.07161), AIOpsLab, ITBench,
     commercial systems (Komodor Klaudia, Datadog Bits AI, Resolve.ai).
   - §2.2 Code-as-policy & Code World Models — Code as Policies (Liang 2023), Meta CWM
     (2025); positions our `sim/engine.py` as an external deterministic world model.
   - §2.3 AutoHarness / harness synthesis — frames `rex/harness_synth.py` +
     `rex/tree.py::thompson_search` as a searched verifier; anchors to TestGen-LLM /
     search-based test generation; reports seed 66.7%→synth 89.7%→hand 94.9% held-out.
   - §2.4 REx / refinement search — maps `rex/tree.py`'s Beta-posterior Thompson tree to
     REx; contrasts Reflexion/Self-Refine/ToT; highlights the SME-vs-no-oracle ablation.
   - §2.5 FIREBALL transfer — D&D `state_before→action→state_after`; flagged as a
     *pending hypothesis* (C2), not a result.
   - §2.6 RLVR/GRPO/Constitutional AI/LLM-judge — positions the **deterministic diagnosis
     reward** in `rex/scoring.py` against LLM-as-a-judge noise (MT-Bench).
   - §2.7 Statistics — pass@k (Chen 2021), Wilson (1927), McNemar (1947).
   - Summary positioning table (thread → representative work → borrow → new).
2. `artifacts/check_related_work.py` — stdlib validator (coverage + structure).

## Grounding traced to the repo (so positioning is true, not invented)
- `rex/harness_synth.py` docstring literally says "AutoHarness-style SYNTHESIS … Rules
  are DATA, not code … we NEVER exec LLM output … reward is classification accuracy on
  TRAIN labels … HELD-OUT generalization." → §2.3 mirrors this exactly.
- `rex/tree.py` — `Beta(alpha,beta)` per node, Thompson-sample argmax to expand,
  deterministic under `seed`. → §2.4 describes REx with these exact mechanics.
- `rex/scoring.py` — `0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap`; diagnosis
  is the deterministic keyword-set judge; `JUDGE_MODE ∈ {deterministic,llm,hybrid}`. →
  §2.6 reward formula + LLM-judge contrast taken verbatim from the source.
- `PAPER_OUTLINE.md §2/§5` — SREGym contrast, harness numbers, McNemar/Wilson protocol.
- `PAPER_QUESTIONS.md §6` — SREGym arXiv id 2605.07161, commercial systems, the gap.

## Decisions
- AutoHarness/REx kept as paradigm labels (the repo names them) + real adjacent anchors;
  no fabricated venue where uncertain (per grill + ouroboros).
- C2 transfer explicitly marked pending.
- No shared core file edited — everything lives under `experiments/ralph_outputs/F1/`.
