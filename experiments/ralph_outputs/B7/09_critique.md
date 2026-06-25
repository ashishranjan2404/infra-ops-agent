# 09 — Honest Critique

## What's weak
1. **Keyword classifier precision.** The biggest weakness: "bad_deploy" over-fires
   (false positives from resource_exhaustion=13, saturation=14) because remediation
   verbs ("rollback", "deploy", "version") are common in answers regardless of true
   cause. This depresses overall accuracy to 0.213 and makes per-category recall
   noisy. A reviewer will rightly attack the vocab as brittle.
2. **Free-text answers are not structured diagnoses.** The HUD `answer` field is a
   full narrative; the agent often lists MULTIPLE causes ("traffic surge ... then
   FD limit ... not a code regression"). Classifying a multi-cause paragraph into
   one category is inherently lossy — the metric may penalize a correct-but-verbose
   diagnosis. The cleaner signal would be a dedicated `root_cause` field, which the
   REx plans have but these exported trajectories do not.
3. **"unknown" gold rows.** 4 records have `true_category == "unknown"`; scoring
   them is ill-defined (we count an "unknown" prediction as correct there, which is
   generous). Small (2% of data) but worth flagging.
4. **Decoupling uses a reward>=0.5 proxy for "resolved".** For the HUD export
   there's no explicit `resolved` bool, so the decoupling % depends on that
   threshold. The direction (large disagreement) is robust, but the exact 43.1%
   would shift with the threshold.

## What a reviewer attacks first
- "Your accuracy measures your keyword list, not the agent." Rebuttal: the YAML
  gold-description self-test hits 0.875, so the classifier recovers gold when the
  text IS clean; the gap on real answers is the agents' verbosity, which is itself
  a finding. Still, a sharper classifier (or scoring against a structured field)
  would strengthen the claim.

## What's missing / not done
- Not wired into `rex/eval_pass_at_k.py` (forbidden: shared-core edit). Only a
  documented one-call integration in 06.
- No precision/recall/F1 beyond per-class recall; no top-2 ("did the right
  category appear among the answer's categories") which would better fit
  multi-cause narratives.
- Not run against REx plan logs (which carry a clean `root_cause` field) — those
  weren't in a single consolidated file; the HUD export was the best available
  consolidated real dataset.

## Honest bottom line
Deliverable is real, hermetic, tested, and runs on real data. The metric is
correct and useful as a DECOUPLED diagnosis signal (the 43.1% disagreement proves
the point). Its absolute accuracy number is limited by a deliberately simple,
interpretable classifier over verbose free text — a known, documented tradeoff,
not a hidden defect.
