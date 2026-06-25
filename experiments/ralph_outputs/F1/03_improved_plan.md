# 03 — Improved Plan (post-grill)

## What changed vs. 01_plan
1. **Citation discipline (accepted REV's hard line).** No fabricated venues/DOIs where
   uncertain. "AutoHarness" and "REx" are kept as the **paradigm labels the repo's own
   docstrings use**, each attached to its real underlying mechanism and to verifiable
   adjacent work (search-based / LLM test generation; bandit-style refinement search).
   Conservative attribution rather than an invented citation.
2. **Section balance (accepted PSRE + RLE).** Two load-bearing halves: a strong
   §2.1 SRE-benchmark/substrate contrast *and* a reward/transfer-heavy §2.4–2.6. Neither
   dominates.
3. **Headline novelty made explicit (accepted RLE).** The RLVR subsection now contrasts
   our **deterministic** diagnosis reward directly against **LLM-as-a-judge** noise — the
   actual contribution, not "we ran GRPO."
4. **Summary positioning table added (accepted DOL).**
5. **Exact statistical tests named (accepted REV):** Wilson 1927, McNemar 1947, pass@k
   (Chen et al. 2021), in a dedicated §2.7.
6. **Validator scoped (accepted DOL):** checks citation *coverage* and document
   *structure*, NOT metric/DOI correctness — a script cannot verify a real DOI; accuracy
   is guaranteed by describing mechanism.

## Rejected critiques (and why)
- **RLE: down-weight the SRE/benchmark contrast.** Rejected. PSRE's rebuttal is correct —
  the SRE-benchmark contrast is what makes a *sim* believable to a skeptical reviewer; if
  it's weak the paper reads as "GRPO on a toy." Kept §2.1 strong.
- **SMR: lean fully on the repo's AutoHarness/REx naming as if canonical.** Partially
  rejected — kept the names but refused to assert a canonical venue we can't verify
  (REV). Net: names as paradigm labels only.

## Final deliverable shape
`related_work.md` with: intro paragraph (maps cites → C1/C2/C3) + §2.1 SRE harnesses +
§2.2 code-as-policy/CWM + §2.3 AutoHarness/harness-synthesis + §2.4 REx/refinement +
§2.5 FIREBALL transfer + §2.6 RLVR/GRPO/Constitutional-AI/LLM-judge + §2.7 statistics +
summary table. Validated by `check_related_work.py`.
