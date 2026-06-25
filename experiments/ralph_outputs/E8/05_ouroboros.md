# E8 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "the statistician"
**Problems found:**
1. The two-sample power formula assumes the comparison is *between two data sizes* with
   per-record reward sd. But an SFT-scaling sweep usually compares a *trained policy's*
   mean reward on a FIXED eval set across N — the unit of variance is the eval-set mean,
   not a single training trajectory. So `required_n_for_effect` answers "how many EVAL
   rollouts to detect δ", which is necessary but is **eval N, not training N**. The spec
   must say this explicitly or it answers the wrong question.
2. sd=0.22 is borrowed from a HUD eval of *frozen* models, not from policies trained on
   N-sized subsets. It's a stand-in.

**Fix applied:** Docstring + 04_spec now state `required_n_for_effect` returns **eval-rollout
N** to detect a reward gap (the measurement budget for any single sweep point), and
08_verification separates *training N* (the headline, blocked) from *eval N* (computable).
sd labelled as an estimate from the frozen-model half.

## Engineer B — "the data engineer"
**Problems found:**
1. Nesting claim: largest-remainder apportionment can shift a stratum's quota by ±1
   between N points, so a record at the prefix boundary can drop out → nesting is
   *approximate*, not exact. Asserting exact ⊂ would be wrong.
2. `scenario_id` is in the family-key fallback list AND families already come from
   `incident`; if a corpus only had `scenario_id`, every record could be its own family →
   strata explode to singletons and apportionment degenerates.

**Fix applied:** (1) Test asserts >0.8 overlap, not 100% — nesting documented as
"near-subset". (2) Fallback order puts `incident`/`failure_mode`/`family` before
`scenario_id`; real corpus uses `incident` (34 families, healthy). Documented as a known
edge for pathological corpora.

## Engineer C — "the reviewer who hates dead code"
**Problems found:**
1. `fit_learning_curve` and the fit-callback path are never exercised on REAL data (no
   trainer) — risk of shipping untested branches that rot.
2. The `knee_N_95pct` from the demo was 56M — absurd; if anyone copies the demo they'll
   quote nonsense.

**Fix applied:** (1) Tests cover the fitter on synthetic points and the callback wiring
with a fake deterministic fit, so both branches are exercised and green — but every such
output is explicitly labelled illustrative, never written into result.json. (2) The 56M
demo is shown in 07 with a loud "ILLUSTRATIVE — do not cite" caption; it actually *proves*
the point that 4 noisy points can't pin a knee, which is why the real curve is blocked.

## Final filtered spec
Unchanged signatures; clarifications added: (a) `required_n_for_effect` = **eval-rollout**
N; (b) nesting is **near-subset** (>0.8); (c) family-key precedence avoids `scenario_id`
fragmentation; (d) any curve/knee output is illustrative until a real fit callback exists.
