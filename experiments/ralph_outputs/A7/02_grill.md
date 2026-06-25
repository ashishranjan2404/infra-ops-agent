# A7 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE ·
**AAAI** AAAI Reviewer · **RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial takes
- **SMR:** A static heuristic `expected_pass_rate` is a *prior*, not a measured
  pass rate. Fine for stratification, but the name will mislead readers into
  thinking it's empirical. Either rename or label it loudly as a prior.
- **PSRE:** From an on-call view the real difficulty driver is "is the loudest
  alert the cause?" and "how deep is the smoking gun buried?". If those two
  dominate the score, I trust it. Topology node count alone is a weak proxy.
- **AAAI:** Where's the validation? A difficulty metric with no correlation to
  observed outcomes is an unfalsifiable assertion. I want at least a sanity
  ranking and a stated limitation that it's uncalibrated.
- **RLE:** For curriculum I don't strictly need calibrated probabilities — I
  need a *monotone ordering* I can sample easy→hard. Ordinal correctness beats
  absolute accuracy here. Give me buckets.
- **DVO:** Whatever you do, do NOT write into the source YAMLs in a parallel
  Ralph run — you'll race other workers. Sidecar only. And make it idempotent.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree that the misleading name is the main problem.
  Renaming is cosmetic. The substantive risk is if the *ordering* is wrong.
  Spend effort on face-validity of the ranking, not on nomenclature.
- **SMR → RLE:** Hard disagree. If you ship `expected_pass_rate=0.43` and
  someone plots it against measured pass@1 expecting agreement, you've created
  a false benchmark — that's worse than a missing field. Naming *is* substance
  when the field implies an empirical quantity it doesn't have.
- **PSRE → AAAI:** Demanding empirical validation is a non-starter — there are
  **no labelled pass rates in this corpus**. Blocking on validation we can't do
  means shipping nothing. A documented, auditable heuristic is the correct
  deliverable; calibration is future work, not a precondition.
- **AAAI → PSRE:** I'll accept "no labels," but then the burden shifts: every
  weight must be transparent and the score must expose its breakdown so a
  reviewer can contest individual terms. A black-box heuristic is unacceptable
  even without labels.
- **DVO → SMR:** Your rename debate is bikeshedding next to reproducibility.
  If two runs of the script give different numbers, nothing else matters. Pin
  determinism (sorted glob, no RNG) before arguing about a field name.

## Round 3 — synthesis
Consensus reached:
1. Keep the field name `expected_pass_rate` (it's the task spec), but ship the
   `schema` block in JSON stating explicitly it is a **model-agnostic prior**,
   and document the uncalibrated limitation in 09 (resolves SMR vs RLE).
2. Weight the two SRE-salient traps (`loudest_alert_not_cause`, `cascades`) and
   `buried_under` depth heavily; topology is a minor term (adopts PSRE).
3. Emit a full per-component breakdown in JSON so weights are auditable
   (adopts AAAI).
4. Provide `difficulty_bucket` easy/medium/hard for ordinal curriculum use
   (adopts RLE).
5. Strict determinism + sidecar-only output, idempotent rerun (adopts DVO).
6. State the no-labels blocker honestly; calibration deferred (adopts PSRE/AAAI).
