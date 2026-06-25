# A8 — 09 Critique (honest)

## What a reviewer will attack
1. **The COMPANIES list is hand-curated and corpus-specific.** Novelty hinges on a
   hardcoded vendor token set. A new training incident from a vendor not in the
   list would not trigger Tier 2. Mitigation today: the list covers every vendor
   actually present in the 34 training incidents; but this does not generalize to a
   growing corpus without maintenance. A more robust version would derive the
   company axis from the union of training tokens automatically.
2. **Token-level matching is shallow.** Two incidents with totally different words
   but the same causal mechanism (e.g. a paraphrased synthetic "oom_kill" vs
   cidg "media_oom_leak") are only caught via the failure_class flag, which is SOFT
   by default. So the *default* held-out set can contain incidents whose mechanism
   was seen in training (different instance, same class). This is intentional
   (we want to measure within-class generalization) but a strict reviewer will
   demand the `--strict-class` split (13 incidents) for the headline number.
3. **No semantic/embedding check.** We do not embed scenario descriptions and
   threshold cosine similarity. A determined leak (same root_cause prose, renamed)
   could survive. The guard is lexical, not semantic.
4. **Held-out N is modest (15, or 13 strict).** Confidence intervals on pass@k over
   13–15 incidents are wide. This is a *coverage* set, not a high-power benchmark.
5. **All cascade incidents are excluded.** The held-out set has zero `cascade`
   coverage because every cascade scenario derives from a real company in training.
   So we cannot measure held-out generalization on multi-hop cascades at all —
   a genuine gap. Fixing it requires authoring *new* cascade incidents from
   organizations/events absent from training.

## What's weak / blocked
- We did NOT run the actual eval (pass@k) on the held-out set — that needs the
  scoring harness + model rollouts and is out of scope for "build the split". The
  split is the deliverable; downstream eval is a follow-up (e.g. feed
  `held_out` into `rex/eval_pass_at_k.py`).
- failure_class strictness is a policy choice we punted to a flag rather than
  resolving definitively.

## Honest bottom line
The deliverable is a **real, re-runnable, auditable** contamination guard and a
defensible held-out manifest, with the contamination *measured* not asserted. Its
weaknesses are lexical-only matching and a maintenance-bound company list; both are
documented and bounded by the fixed 32/34-incident corpus this task targets.
