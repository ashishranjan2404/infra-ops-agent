# 09 — Honest critique

## What's weak
1. **Small rep counts.** A1 has 3 reps/incident, A2 has 5. A per-incident pass@1==0 off
   3 reps × 5 conditions is suggestive, not conclusive. The "unsolvable" flag is an
   operational triage label; a skeptic is right that it isn't a population-level claim.
   Mitigation in place: every cell carries `n` and `passes`; no impossibility language.
2. **Conditions are correlated.** The 5 conditions share a proposer model, so treating the
   pooled per-incident samples as independent Bernoulli trials would overstate confidence.
   We deliberately do NOT compute a per-incident CI for this reason — but that also means
   the flag has no attached uncertainty band.
3. **Only two models / two thresholds-of-one.** Cross-model agreement on the 3 unsolvable
   incidents is encouraging but n=2 models. A third model could move them to "partially."
4. **Threshold sensitivity untested.** Everything is at threshold 0.8 (inherited from the
   sources). An incident at mean_reward 0.78 is "unsolvable" here but would flip at 0.75.
   The tool surfaces mean_reward per cell so a reader can see borderline cases, but it does
   not sweep the threshold.
5. **Different incident sets per source.** A1 has 42 incidents, A2 has 30; only the
   overlap is truly comparable cross-model. The by-family rollup mixes both, so family
   counts are model-weighted, not a clean per-incident union.

## What a reviewer attacks first
- "0/15 is not independent — your unsolvable claim is overconfident." → addressed by
  operational wording + disclosing n; we do not claim statistical impossibility.
- "Why no threshold sweep?" → fair; out of scope for this slice, noted as future work.

## What's missing / future work
- A `--threshold-sweep` mode to show solvability as a function of the pass threshold.
- Restrict cross-model rollup to the incident intersection for a clean comparison.
- Pull in additional model result JSONs as they land (the tool already accepts N inputs).

## Honest bottom line
The deliverable does exactly what the task asked — per-incident pass@1/pass@k per condition
with an unsolvable flag — on real A1/A2 data, and produces a defensible cross-model signal
(3 incidents fail under both models; 41 are learnable-but-hard). The main caveat is rep
count / independence, which is disclosed rather than hidden.
