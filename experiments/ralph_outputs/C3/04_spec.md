# C3 — 04 Spec

## Inputs
- A8 manifest: `experiments/ralph_outputs/A8/artifacts/heldout_manifest.json`
  → `held_out: list[str]` (15 cidg ids, certified novel). Used as the novel universe.
- Shared core (imported, unmodified): `rex/harness_synth.py`, `rex/tree.py`, `rex/harness.py`.

## Split (constants in the runner)
```
TRAIN   = [auth_cert_expiry, billing_disk_fill, checkout_bad_rollout,
           conntrack_exhaustion, facebook_bgp_backbone, gke_ip_exhaustion,
           ingest_fd_exhaust, kafka_poison_pill, payments_dep_revoked,
           search_cpu_starve]                                   # 10
HELDOUT = [azure_leapyear_cert, firefox_addon_cert, knight_capital_conflict,
           media_oom_leak, redis_cache_flush]                   # 5
```
Invariants (asserted at runtime): `TRAIN ∩ HELDOUT = ∅` and
`(TRAIN ∪ HELDOUT) ⊆ A8.held_out`.

## Data structures (reused from rex/harness_synth.py)
- `labeled_examples(name) -> list[ {incident, tool, target, features, should_block, hazard} ]`
- `features` dict over FEATURES = {tool, treats_forbidden_category, leak_active,
  last_ready_node_op, at_replica_limit, rollback_without_deploy}.
- A **rule** (DATA): `{match_tools: list[str], conditions: [{feature, op, value}],
  block: bool, reason: str}`; `op ∈ {==, !=}`. First matching block-rule wins, else allow.

## Function signatures (runner)
- `_load_novel_universe() -> list[str]` — reads A8 manifest `held_out` (fallback: split union).
- `main() -> int` — asserts invariants; builds train/held examples; prints hazard
  coverage; runs `thompson_search(propose=_propose, evaluate=train_score, budget, seed=0,
  stop_at=1.0)`; scores best on TRAIN+HELDOUT for {seed, synthesized, hand-written};
  prints held-out mistakes + leakage check; dumps JSON.
- `_propose(parent)` — sets `hs.MODEL = $C3_MODEL` around `hs.propose_ruleset(parent, train_ex)`.

## Reward (reused) — `train_score`
`base = 1 − (2·FA + 1·FB)/maxerr` minus `λ·n_conditions` (λ=0.003 tie-breaker toward
simpler rules). FA (false-allow, dangerous) weighted 2×.

## Output JSON contract — `novel_synth_result.json`
```
{ experiment, model, budget,
  a8_novel_universe: [15 ids], train: [10], heldout: [5],
  rules: [rule, ...],
  hazard_scope: { hazard: "GENERALIZABLE"|"UNSEEN-in-train (out-of-scope)"|"train-only" },
  table: { <harness>: { train:{accuracy,false_allow,false_allow_rate},
                        heldout:{...} } },
  node_scores: [float, ...],
  heldout_false_allow: [[incident,tool,target,hazard], ...],
  heldout_false_block: [...],
  leakage_disjoint: bool }
```

## Test cases (07)
- T1 `python3 -c import` of the runner module → no import error.
- T2 full run → exits 0, writes JSON, prints leakage `disjoint: True`.
- T3 stability → run twice, held-out accuracy + FA% identical.
- T4 provenance → corrupt the split (inject a non-novel id) → AssertionError.
- T5 no core edits → `git status` shows only files under `experiments/ralph_outputs/C3/`.
