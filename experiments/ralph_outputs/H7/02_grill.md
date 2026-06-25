# 02 — Grill (5 personas, 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take
- **SMR:** A registry is only useful if every row is provenanced. Each model must cite the
  exact file/line it was harvested from, otherwise it's a vibe doc. And `eval_pass_at_1`
  must be a *measured* number or null — never a guess.
- **PSRE:** From an ops view the registry must answer "which models can I actually invoke
  right now and which throw 5xx?" The Qwen3.5-4B that 502s and the 30B that died on a
  Tinker 503 are operationally distinct from a healthy frozen Claude. Encode status.
- **AAAI:** For a paper, the interesting claim is the eval-vs-trainable split: closed models
  are baselines you cannot GRPO. The registry should make that dichotomy first-class
  (a `role` field), not bury it.
- **RLE:** I want training trajectory, not just a label. start→end mean reward per run tells
  the real story (8b went *down*, that's the headline finding). Put those numbers in.
- **DOL:** Keep it a flat JSON + a zero-dependency CLI. No DB, no server. It has to run on a
  laptop with stdlib. And make it filterable so CI can grep it.

## Round 2 — react to another persona BY NAME (genuine disagreement)
- **RLE → SMR:** I disagree with SMR's "pass@1 or null" purism taken to the extreme. Null
  everywhere makes the registry look empty and useless. We DO have a real per-model reward
  signal — the frontier baseline/REx means. Use *those* as the populated metric and stop
  pretending the registry has no numbers.
- **SMR → RLE:** Pushback accepted only partway. Frontier mean reward is NOT pass@1 — they're
  different metrics. If you shove a mean-reward number into a `pass@1` column you've committed
  the exact fabrication I warned about. Keep separate columns: `eval_pass_at_1` (null, honest)
  AND `frontier_baseline_mean` / `frontier_rex_mean` (real). Don't conflate.
- **PSRE → AAAI:** AAAI's role split is fine for a paper but operationally insufficient. "eval"
  vs "trainable" doesn't tell me the 30B is *dead*. I need a `training_status` orthogonal to
  role: frozen / forked / trained / flat / aborted. A model can be trainable AND aborted.
- **DOL → RLE:** RLE wants per-step reward arrays in the registry — no. That bloats the JSON
  and duplicates `opensre-traj/runs/*.jsonl`. Store only start/end + a `source` pointer to the
  full run file. Single source of truth for the raw curve.
- **AAAI → SMR:** Agree on provenance but warn against over-engineering: SMR's instinct to
  add confidence intervals / seeds per cell is scope creep for a registry. A registry indexes
  models; it is not the eval harness. Point to the eval artifacts instead.

## Round 3 — synthesis
Consensus reached:
1. Two orthogonal axes: `role` (eval | trainable) and `training_status`
   (frozen | forked | trained | flat | aborted). (PSRE + AAAI)
2. Keep `eval_pass_at_1` as an honest null column; populate the REAL metric we have in
   separate `frontier_baseline_mean` / `frontier_rex_mean` columns. No conflation. (SMR + RLE)
3. Per-row `source` field citing repo file(s)/line(s); no raw reward arrays — point to the
   run jsonl instead. (SMR + DOL)
4. start→end train mean reward per trainable model (the 8b-down / 8b-v2-up / 30b-aborted
   story is the payload). (RLE)
5. Flat JSON + stdlib CLI, filterable, exit-code-correct. (DOL)
