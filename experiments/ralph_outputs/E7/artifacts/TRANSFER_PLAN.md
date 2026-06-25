# Cross-Domain Transfer Experiment Plan (E7)

## Hypothesis
H1: A REx-configured diagnose-then-act policy (frozen LLM + Thompson-sampling
tree, tuned on SRE incidents) **transfers zero-shot** to text-game domains
better than a domain-native non-search baseline.

H0 (null): REx's advantage on SRE is domain-specific; on games it is no better
than a frozen-LLM-in-domain baseline.

## Domains & sources
- **TextWorld** — `pip install textworld`; generate games with known
  walkthroughs (`tw-make`). Cheap, gold known, difficulty knobs.
- **Jericho** — `pip install jericho` + Z-machine ROMs (license-gated; user
  supplies). Long-horizon, human-authored distractors.
- **ALFWorld** — `pip install alfworld`; tests embodied/grounded transfer.

## Conditions
| condition | policy | domain knowledge |
|---|---|---|
| C0 random-admissible | sample from `available_actions` | none |
| C1 frozen-LLM in-domain | LLM, no search, domain prompt | in-domain |
| C2 REx zero-shot from SRE | REx tree, SRE-tuned, no game tuning | cross-domain |
| C3 REx + light in-domain calib | REx, few-shot in-domain | in-domain |

Transfer is supported iff **C2 > C1** (and ideally C2 ≈ C3) on held-out games.

## Metrics (plural — per grill synthesis)
1. **episode-success rate** (`solved`).
2. **deterministic-judge pass-rate** via `rex/scoring.deterministic_judge` on
   `to_sre_scoring_inputs()`.
3. **action-overlap-with-gold** (Jaccard of `actions` vs walkthrough).
4. **normalized game score** = score / max_score.
Report mean ± bootstrap 95% CI over ≥3 seeds (mirrors A1 protocol).

## Ablations
- **A-oracle:** with vs without `available_actions` handicap (count
  `meta["warnings"]` to detect off-oracle actions).
- **A-distractor:** inject extra `distractors`, measure success degradation —
  the analogue of SRE red-herrings.

## Pipeline (using the shipped adapter)
```
raw episode log --(trajectory_adapter.adapt)--> CanonicalTrajectory
   --.to_sre_scoring_inputs()--> rex.scoring.deterministic_judge / mechanism_score
   --aggregate--> per-condition table (reuse rex/eval_pass_at_k.py style)
```

## Caveats (kept out of the schema, per grill)
- **Irreversibility:** SRE incidents are irreversible; IF games allow
  save/restore. Game transfer is *necessary, not sufficient* evidence for prod.
- **Oracle handicap:** admissible/valid-action lists do not exist at real
  inference; the headline number must be the off-oracle (A-oracle) variant.
- **Lexical judge:** the deterministic judge is lexical; pair it with the LLM
  judge (`rex/scoring.judge_diagnosis`) for game text where vocabulary differs.

## Proposed (NOT applied) core change
Add game domains to the eval CLI by registering a loader that calls
`trajectory_adapter.adapt(domain, raw)` — a ~15-line addition to a NEW file
`rex/transfer_eval.py`, leaving existing core untouched. Documented here only.

## Blocker
Live run requires `textworld`/`jericho`/`alfworld` installs + ROMs/network,
unavailable in this sandbox. Deliverable is the adapter + protocol; the numbers
run is the documented blocker.
