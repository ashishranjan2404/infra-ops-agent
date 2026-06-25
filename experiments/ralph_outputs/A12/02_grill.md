# A12 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DEVO** (DevOps Lead).

## Round 1 — initial take
- **SMR:** A static structural proxy for difficulty is a fine *starting* curriculum,
  but the literature (Bengio 2009; teacher-student curricula) shows the only
  difficulty that matters is *difficulty as seen by the learner*. A hand-weighted
  sum of YAML booleans is a prior, not ground truth. Acceptable if labeled as such.
- **PSRE:** From an incident-response view the chosen signals are exactly right:
  hidden root cause, loud-alert-not-cause, buried evidence, and "naive fix worsens
  it" (hysteresis) are *precisely* what makes a real outage hard for a human SRE.
  The proxy has real domain validity.
- **REV:** Where do the weights come from? `loud_not_cause=2.5`, `hidden=2.0` — these
  are unjustified magic numbers. A reviewer will ask for an ablation or correlation
  against measured pass-rate. Without it this is "difficulty by fiat."
- **RLE:** For curriculum *learning* I mostly need a monotone ordering and the
  ability to bucket (anti-curriculum, mixed). A scalar + rank gives me that. But I
  want the per-feature vector exposed so I can re-weight without re-reading YAMLs.
- **DEVO:** Is it reproducible and cheap? If it's a deterministic script over files
  in the repo, yes. Don't make it depend on a live model or HUD — that would make
  the curriculum itself nondeterministic.

## Round 2 — react to another persona (genuine disagreement)
- **SMR → PSRE:** I disagree that domain validity is enough. PSRE, your "this is
  what's hard for a human SRE" is an *anthropomorphic* prior. The policy here is a
  frozen LLM in a sim; what's hard for a Claude-class model is empirically often
  the *opposite* — models breeze through multi-hop cascades they've seen in
  postmortems and choke on a boring single-leaf OOM with a misleading metric. Your
  signal could be anti-correlated with model difficulty.
- **PSRE → SMR:** Counter: the simple leaf incidents are *clones* (3 mechanisms × 5
  services). They are trivially easy by construction — same gold root, renamed node.
  No model "chokes" on those. So at minimum the simple-vs-real split is correct, and
  that's 80% of the curriculum's value. Your anti-correlation worry only bites on the
  fine ordering *within* the hard tier.
- **REV → RLE:** RLE says "I just need a monotone order" — that's too low a bar for a
  publishable result. If the ordering is arbitrary, curriculum vs random-order will
  show no significant gap and the whole experiment is a null. The weights MUST be
  defensible or empirically derived, otherwise A12 produces an artifact nobody can
  cite.
- **RLE → REV:** Disagree on scope. A12's deliverable is *the ordering*, not the
  curriculum-learning result. Deriving empirical difficulty needs a full pass@k
  sweep across 36 incidents × N models — that's a different, expensive task. Shipping
  a documented static prior NOW unblocks the experiment; we refine weights when
  pass@k data exists. Blocking on empirical weights is scope creep.
- **DEVO → REV:** Agree with RLE against REV. I'd rather have a deterministic,
  re-runnable prior in the repo today than a "perfect" empirical curriculum that
  depends on a 30-minute model sweep every time the scenario set changes.

## Round 3 — synthesis
Consensus: ship the **static composite ordering now**, but (1) label it explicitly
as a *prior*, not measured difficulty; (2) expose the full per-feature vector and
the weight dict in the output so it's re-tunable / ablatable; (3) lean on the one
thing everyone agrees is correct — the **simple-leaf vs real-outage split** — and
treat the within-tier order as provisional; (4) keep it model-free and
deterministic. Note the open question (correlate with empirical pass@k) as future
work in 09_critique. REV's "magic weights" critique is accepted to the extent that
we document and expose weights; rejected as a *blocker* because empirical
calibration is a separate task.
