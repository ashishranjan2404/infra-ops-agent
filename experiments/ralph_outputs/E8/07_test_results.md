# E8 — 07 Test Results

## Unit tests
```
$ python3 -m pytest test_fireball_sweep.py -q
.............                                                            [100%]
13 passed in 0.11s
```
All 13 pass, including the two anti-fabrication guards:
- `test_no_fit_means_blocked_and_no_scores` — no fit ⇒ `blocked:true`, all scores None.
- `test_learning_curve_needs_4_points` — fitter returns None on <4 points.

## Real-corpus profile + power analysis
```
$ python3 fireball_sweep.py --profile-only
corpus:        /Users/mei/rl/opensre-traj/out/trajectories.jsonl
n_records:     319
n_families:    34
per_difficulty:{'3': 100, '4': 201, '5': 18}
mean_steps:    14.59
POWER (δ=0.05, sd=0.22): per-arm eval N = 304
```

Power table (sd=0.22, α=.05, power=.80), eval-rollout N per arm:
```
δ=0.10 -> 76   (both arms 152)
δ=0.07 -> 156  (both arms 312)
δ=0.05 -> 304  (both arms 608)
δ=0.03 -> 845  (both arms 1690)
δ=0.02 -> 1900 (both arms 3800)
```

## Real-corpus sweep (THE BLOCKER, shown honestly)
```
$ python3 fireball_sweep.py --n-grid 1000,5000,10000,25000,50000 --seeds s1,s2 --out-dir sweep_manifests
blocked: True
learning_curve: None
  N=  1000 -> actual= 319  score=None  fams=34
  N=  5000 -> actual= 319  score=None  fams=34
  N= 10000 -> actual= 319  score=None  fams=34
  N= 25000 -> actual= 319  score=None  fams=34
  N= 50000 -> actual= 319  score=None  fams=34
```
**Every requested N (1k–50k) caps at the corpus size of 319.** The harness degrades
honestly: it still writes manifests and the power analysis, marks the run `blocked:true`,
and emits NO scores and NO curve. This is the concrete materialization of the Fireball-data
blocker (below).

## Fixture validation (harness works at scale when data exists)
```
$ python3 make_fixture.py --n 2000           # wrote 2000 records
$ python3 fireball_sweep.py --corpus fixture_corpus.jsonl --n-grid 100,500,1000,2000 --seeds s1
  N=  100 -> actual=  100  fams=8  diff={'3': 30,  '4': 60,   '5': 10}
  N=  500 -> actual=  500  fams=8  diff={'3': 147, '4': 302,  '5': 51}
  N= 1000 -> actual= 1000  fams=8  diff={'3': 294, '4': 605,  '5': 101}
  N= 2000 -> actual= 2000  fams=8  diff={'3': 589, '4': 1206, '5': 205}
```
Stratification holds (the .3/.6/.1 difficulty mix is preserved at every N), and uncapped
N values are honored when the corpus is large enough.

## Curve fitter — ILLUSTRATIVE ONLY, DO NOT CITE
```
$ # 4 MADE-UP points, purely to exercise the fitter:
demo=[(1000,0.40),(5000,0.52),(10000,0.58),(50000,0.62)]
fit: {'a':0.76,'b':1.35,'c':0.2,'sse':0.00185,'asymptote':0.76,'knee_N_95pct':56591455,...}
```
The knee of 56M is absurd — that is the *point*: four noisy points cannot pin a knee. This
output is fabricated input for a wiring test and is never written to result.json.

## Blocker (Fireball data)
- **Volume:** the real Fireball-format corpus is **319 trajectories**, ~100× below the 1k
  floor and ~150× below the 50k ceiling of the intended sweep. The data-scaling *training*
  curve cannot be produced because the data to subset above 319 does not exist in-repo.
- **Source corpus / trained model absent:** consistent with
  `experiments/results/P7_fireball_status.md` — the original FIREBALL `incidents.jsonl` and
  the fireball-trained model slug are not in this repo.
- **No fit callback:** even at 319, computing real (N, score) points needs a trainer +
  evaluator wired as the `FitCallback`; those live in shared core files
  (`opensre-traj/train_rft_v2.py`, `rex/eval_pass_at_k.py`) which were not edited.
- **Honest consequence:** we deliver the runnable harness + power-analysis N + the
  blocker. We do **not** fabricate a scaling curve.
