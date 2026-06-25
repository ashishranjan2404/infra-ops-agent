# D9 — 04 Spec

## Inputs
- `A12/artifacts/curriculum_order.json`:
  `{signal, weights, order_easy_to_hard:[id], n, incidents:[{id,yaml,family,
  failure_class,difficulty,features,rank}]}`. `order_easy_to_hard` is
  non-decreasing in `difficulty`. 51 incidents, difficulty 0.9–17.0.

## Data structures
### Stage
```
{ stage:int, epoch:int, newly_unlocked:[id],
  active_incidents:[{id, weight:float, difficulty:float}],
  n_active:int, samples_this_stage:int }
```
### Schedule (build_schedule output)
```
{ order:"curriculum|random|anti", n_stages:int, rehearsal:float, seed:int,
  samples_per_incident:int, source_signal:str, n_incidents:int,
  total_sample_budget:int, ordered_ids:[id], stages:[Stage] }
```
### TrainingConfig (training_config output)
```
{ experiment, base_model, algorithm:"GRPO", reward, group_size:8, lr:1e-6,
  kl_coeff:0.02, max_tokens:4000, epochs_per_stage:1,
  advance_criterion:{metric,threshold:0.55,patience_epochs:2,note},
  curriculum:Schedule, blocker:str }
```
### ComparisonReport (compare output)
```
{ kind, model_note, n_incidents, n_stages, rehearsal,
  sim_params:{LR,SIGMA,K,C0},
  results:{ <order>:{order, final_mean_reward, final_mean_reward_std, auc,
                     n_seeds, stage_eval:[{stage,competence,mean_reward}]} },
  verdict:{ curriculum_auc, random_auc, auc_delta, curriculum_beats_random:bool,
            final_delta } }
```

## Function signatures
- `load_order() -> dict` — load+require A12 json (FileNotFoundError if missing).
- `_bands(ids:list, n_stages:int) -> list[list]` — contiguous near-equal split.
- `build_schedule(order="curriculum", n_stages=5, rehearsal=0.3, seed=1234,
  samples_per_incident=8) -> Schedule`.
- `training_config(n_stages=5, rehearsal=0.3, seed=1234) -> TrainingConfig`.
- `simulate_run(order, n_stages, diff, seed, rehearsal=0.3) -> dict` — competence
  proxy; eval over the WHOLE set every stage.
- `compare(n_stages=6, seeds=5, rehearsal=0.3) -> ComparisonReport`.

## Simulation model (documented, not measured)
- competence `c` starts at C0=0.5.
- per training touch: `c += LR*weight*exp(-((d-c)/SIGMA)^2)` (Gaussian learnable band).
- eval reward proxy per incident: `sigmoid(K*(c-d))`; stage reward = mean over all 51.
- params: LR=0.18, SIGMA=3.5, K=0.9, C0=0.5 (fixed, in report).

## Test cases (pytest)
1. A12 order loads, lengths consistent, n≥30.
2. curriculum order is non-decreasing difficulty.
3. bands cover all ids, no overlap.
4. progressive unlock: active set grows; newest weight 1.0, old 0.3.
5. random shuffle deterministic per seed; differs across seeds.
6. random & curriculum share the same incident set.
7. training_config embeds schedule + blocker; algorithm GRPO.
8. all sim rewards ∈ [0,1].
9. curriculum AUC > random AUC (core hypothesis).
10. anti AUC ≤ curriculum AUC.

## Real-eval seam
Replace `simulate_run` body with: for each stage, roll out the model on its
`active_incidents`, then eval over all incidents via
`rex.scoring.score_plan(plan, scenario, sim_result)`; reuse band/metric/report
code verbatim.
