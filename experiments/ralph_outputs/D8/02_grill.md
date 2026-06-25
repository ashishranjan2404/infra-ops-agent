# D8 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial takes

**SMR:** The thesis is a structural-transfer argument: Fireball turns are
`s -> a -> s'` triples, same shape as incident steps. Plausible, but SFT on
imitation of D&D combat optimizes next-token fit to D&D text, not the *transition
dynamics* abstractly. The transfer mechanism is hand-wavy. We need the adapter to
surface the transition structure explicitly (STATE_BEFORE/ACTION/STATE_AFTER),
not just dump raw narration, or there's nothing to transfer.

**PSRE:** I care that the eval is on *real* cascade incidents and that "cascade
vs simple" is defined by something other than vibes. If the split is post-hoc
cherry-picking we've proven nothing. Also: a D&D model giving SRE advice is a
great way to hallucinate confident nonsense during a real incident.

**REV:** Claim 2 currently rests on ONE run by Wenji. Single-run, no seeds, no CI.
For AAAI this is a desk-reject unless replicated with multiple seeds and a
baseline that isn't trivially weak. The asymmetry (better on cascade, worse on
simple) is interesting *only if* it's statistically real.

**RLE:** Why SFT and not GRPO? The project's whole framing (train_rft_v2) is GRPO
with a deterministic judge. SFT on Fireball is a different beast — fine, but be
explicit it's imitation pretraining, then GRPO on SRE on top. Also: what's the
`reward` field doing in an SFT example? That's a smell.

**DOL:** Where does the data come from, how big, and can I reproduce the run from
a config? If the corpus isn't in the repo this whole task is blocked and I want
that stated up front, not buried. I also want the pipeline to *fail closed* if
someone points it at the tiny fixture and hits "train for real".

## Round 2 — react to another persona (genuine disagreement)

**RLE @ SMR:** I disagree that explicit STATE/ACTION framing is enough. You're
assuming the model learns dynamics; SFT will mostly memorize D&D surface forms.
The "transfer" you want needs the *eval* to reward multi-hop reasoning, not the
*training* format. Don't oversell the adapter as the mechanism.
> Resolution: agreed the adapter is necessary-not-sufficient; we frame it as
> "expose the transition so SFT *can* fit it", and put the burden of proof on the
> transfer eval, which is in the config — not claimed as done.

**SMR @ REV:** I push back on "desk-reject". A clean single-run *pilot* with a
released scaffold is a legitimate contribution IF we don't overclaim. The bar
you're setting is for the final paper, not for D8's deliverable.
> Resolution: D8 does NOT claim the result; it builds the replication harness.
> REV's multi-seed/CI demand is recorded as the acceptance bar for the rerun.

**PSRE @ DOL:** You want reproducibility from a config, but you're ignoring that
the data is the entire risk. A reproducible pipeline over data we don't have is
theater. I'd rather have a loud blocker than a pretty YAML.
> Resolution: both — the YAML carries `is_real_fireball: false` +
> `min_examples_for_real_run`, so it's reproducible AND fails closed AND screams
> the blocker. DOL conceded the guard matters more than polish.

**REV @ RLE:** The `reward` field in an SFT record genuinely bothered me too. If
it's a Fireball outcome you've leaked a fabricated score. Justify it or drop it.
> Resolution: RLE & REV agreed: rename its *meaning* (in code + docstring) to a
> data-quality/informativeness weight used for loss weighting, explicitly NOT a
> Fireball game score. Documented in the adapter.

**DOL @ PSRE:** Disagree that a D&D model is inherently dangerous in prod — we
never deploy it to prod; it's an offline research artifact evaluated in a sim.
The safety angle is out of scope for D8.
> Resolution: accepted as out of scope; noted for any future deployment story.

## Round 3 — synthesis

Consensus the team will hold D8 to:
1. Adapter must make the `s -> a -> s'` transition explicit (STATE_BEFORE /
   ACTION / RESULT+STATE_AFTER), read fields defensively, skip non-transitions.
2. The `reward` field is a documented data-quality weight, never a game score.
3. The config defines the *transfer* eval (cascade vs simple, pass@1/2/5,
   3 baselines: zero-shot / opensre-trained / fireball-trained) but D8 does NOT
   run it or claim a result — blocked on Wenji's data.
4. Pipeline fails closed on fixture data (`is_real_fireball` guard).
5. Multi-seed + CI is the acceptance bar for the eventual rerun (recorded, not
   met here).
6. Tiny synthetic fixture + unit test prove the adapter mechanically; no
   fabricated Fireball numbers anywhere.
