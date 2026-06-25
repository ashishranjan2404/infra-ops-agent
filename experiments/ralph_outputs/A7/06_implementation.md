# A7 — 06 Implementation

## What I built
A single self-contained, deterministic scorer:
`experiments/ralph_outputs/A7/artifacts/score_difficulty.py` (stdlib + pyyaml).

It reads every `scenarios/cidg/generated/*.yaml` **read-only**, computes
`trap_complexity` and `expected_pass_rate` (+ a `difficulty_bucket`) from
structural signals already in each YAML, and writes two sidecar artifacts into
the A7 artifacts dir:
- `difficulty_scores.json` — full breakdown incl. `schema`, per-incident
  `trap_breakdown` and `pass_rate_penalties` (auditable weights), sorted
  hardest-first.
- `difficulty_scores.csv` — flat `file,id,failure_class,trap_complexity,
  expected_pass_rate,difficulty_bucket` table.

## Key implementation details
- `trap_complexity(d)` / `expected_pass_rate(d, tc)` are pure functions of the
  YAML dict; both return `(score, breakdown)` so every term is inspectable.
- Empty `smoking_guns` guarded; all numeric `.get` calls have defaults and are
  `float(... or 0)`-safe (from the Ouroboros pass).
- Deterministic: `sorted(glob(...))`, no RNG. Idempotent on identical inputs.
- Non-mutating: opens source YAMLs with `'r'` only; writes exclusively into the
  A7 artifacts dir.

## Real run (current corpus = 48 incidents)
```
scored 48 incidents
  expected_pass_rate: min=0.433 mean=0.560 max=0.873
  trap_complexity:    min=0.062 mean=0.593 max=0.791
  buckets: easy=11 medium=23 hard=14
  hardest 5: gitlab-db-deletion, roblox-consul-streaming, aws-s3-typo-capacity,
             monzo-cassandra-compaction, circleci-kubeproxy-iptables  (epr≈0.43)
  easiest 5: media-oom-leak, payments-dep-revoked, fd-exhaust-leaf-shipper,
             cert-expire-leaf-sidecar, mem-leak-leaf-transcoder        (epr≈0.87)
```
NOTE: the corpus grew from 33 → 48 YAMLs *during* this run because other
parallel Ralph workers were generating new scenarios. The scorer re-ran cleanly
and scored the full current set (json count == disk count == 48), demonstrating
it is robust to corpus growth and safe under concurrency (sidecar-only).

## Core-file change I did NOT make (per brief)
A natural follow-up is to surface `difficulty_bucket` in `rex/eval_pass_at_k.py`
for stratified reporting. Per the parallel-safety rule I did **not** edit that
shared file. The sidecar JSON is keyed by `file`/`id` so a consumer can join on
it without any change to the generator or YAMLs.
