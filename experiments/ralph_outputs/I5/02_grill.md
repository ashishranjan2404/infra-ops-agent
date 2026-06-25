# I5 — 02 Grill (Ralph Loop: 5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **AAAI** (AAAI
Reviewer), **RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial takes

**SMR.** The right object is the *advantage*, not the reward. RLVR's failure mode is
degenerate advantage: binary verifier ⇒ within a group either everyone passes or no one
does ⇒ `Std(A)=0` ⇒ no gradient. SME feedback is interesting precisely because it adds
*spread*. So the headline metric should couple alignment AND magnitude — a pure-alignment
metric would miss the flat-reward story.

**PSRE.** From on-call reality: SME feedback is expensive and *bursty*. We don't get a
dense preference on every incident; we get a thumbs-up/down on a handful. The model must
have a **labeling budget** `p`, not assume universal SME coverage. And SMEs are wrong more
than ML people admit — postmortems regularly overturn the on-call's first call. Override
error `eps` is the crux variable, not a footnote.

**AAAI.** For this to be a *proposition* and not a vibe, I need explicit assumptions and a
falsifiable condition. "SME helps" must be operationalized (helps *what* — variance?
bias? steps-to-target?) and there must be a regime where it provably does NOT help.
Otherwise reject as non-novel reward shaping.

**RLE.** Implementation-wise, "reshape the advantage" can mean two different things:
(a) blend rewards then recompute group-centered advantage, or (b) directly add an SME
advantage term. These are not equivalent under group normalization. Pick one and be
explicit, or your sim is ambiguous.

**DOL.** Whatever you build must *run* deterministically with seeds and emit JSON I can
diff in CI. No notebooks, no manual steps, no external services. And keep it numpy-only so
it runs anywhere.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**AAAI → SMR (disagree).** SMR's composite `G = Corr·Std` is *not* a sample-efficiency
quantity — it's a heuristic. A reviewer will hammer that. Multiplying a correlation by a
std has no decision-theoretic meaning; you could inflate `G` by adding pure-magnitude
noise that happens to correlate slightly. I want either a variance-of-the-gradient-
estimator argument OR an explicit disclaimer that `G` is a proxy validated against a
learning curve. Don't dress a heuristic as a theorem.

**SMR → AAAI (partial pushback).** Fair, but you're letting the perfect kill the useful.
A tight PAC-style bound on a frozen-LLM policy-gradient step is out of scope for a one-day
artifact. `G` *is* principled as a first-order proxy: REINFORCE gradient variance falls and
its bias toward truth rises exactly when alignment×spread rises. I'll concede the label:
call it a **proxy**, and back it with a learning-curve sim so the claim is empirical, not
asserted.

**RLE → PSRE (disagree).** PSRE wants `eps` front-and-center, but if we ALSO make `p`
(budget) a free knob, the sim has too many degrees of freedom and the "when does it help"
answer becomes mushy. I'd fix `p` and sweep only `λ × eps`. Disagreement: PSRE is
optimizing for realism, I'm optimizing for a legible crossover.

**PSRE → RLE (counter).** Fixing `p` hides the most actionable lever for an SRE manager —
"is it worth paging the expert?" is a budget question. Compromise: keep `p` a parameter
with a sensible default (0.3), test the `p=0` no-op explicitly, but headline the `λ × eps`
sweep so RLE gets his legible crossover. Both can be true.

**DOL → AAAI (disagree on scope).** AAAI keeps escalating rigor; I'll push back: if the
artifact doesn't run and produce a diff-able number, the proposition is worthless to us.
I'd rather have a *runnable* proxy with passing invariant tests than a beautiful unproven
bound. Ship the sim.

## Round 3 — synthesis

Consensus reached:
- **Object**: reshape *reward then recompute group-centered advantage* (RLE option (a),
  stated explicitly). 
- **Metric**: `G = Corr(A, q_centered)·Std(A)`, **explicitly labeled a proxy** (AAAI/SMR
  compromise), **validated by a learning-curve steps-to-target sim** (DOL/SMR).
- **Variables**: keep `p` (budget) as a parameter with `p=0` no-op test (PSRE), but
  **headline the `λ × eps` crossover** (RLE).
- **Proposition**: must include a regime where SME *hurts* (AAAI) — derive a crossover in
  `eps`/`λ`.
- **Engineering**: numpy-only, seeded, JSON output, invariant tests incl. zero-λ no-op
  (DOL).
