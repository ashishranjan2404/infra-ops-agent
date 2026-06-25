# 02 — Ralph Loop Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take
- **SMR:** A demo video isn't a research contribution, but it's how reviewers form a
  first impression. The risk is theater: a pretty terminal that doesn't run real code.
  Insist the frames come from the actual engine.
- **PSRE:** As an on-call, the only thing I trust is "did the root clear." Show the
  oracle distinguishing a band-aid (restart) from the causal fix (scale). If the demo
  glosses that, it's marketing, not SRE.
- **REV:** I will pause the video and ask "is this cherry-picked / scripted?" If it's
  scripted, SAY SO on screen. A hidden script masquerading as a live agent is a credibility
  landmine.
- **RLE:** Don't burn a live LLM call in the demo — nondeterministic, flaky, needs a key,
  unreproducible for re-recording. Script the trajectory; keep the *environment* real.
- **DVO:** Whatever you ship must run on a clean machine with `python3 file.py`. No asciinema
  dependency in the hot path. Provide a text-transcript fallback.

## Round 2 — react to another persona BY NAME (forced disagreement)
- **RLE → PSRE:** I disagree with PSRE's implied "make it as real as possible = live agent."
  A live agent in the *demo* is a liability. The realness that matters is the *oracle and
  engine*, not the policy being an LLM at record time. Determinism > authenticity-theater.
- **PSRE → RLE:** Pushback. A fully scripted happy-path hides the interesting failure. If you
  script it, you MUST keep the wrong-tool attempt that genuinely fails *in the engine* —
  otherwise you've staged a success and I won't believe the oracle does anything.
- **REV → SMR:** SMR says the video isn't a contribution — I half-disagree. For a *systems*
  paper the demo IS evidence the artifact runs. But ONLY if it's the real artifact. A scripted
  cartoon is worse than no video. So my bar is higher than SMR's, not lower.
- **SMR → REV:** REV wants "SCRIPTED" stamped on screen; I think that's overcautious and ugly
  for a talk opener. Compromise: don't lie that it's live, but the disclosure belongs in the
  storyboard/narration and code docstring, not as a giant watermark over the metrics.
- **DVO → REV:** REV is worried about credibility; I'm worried about it not running at all in
  the room. A `.cast` that needs asciinema installed will fail live. The transcript + a
  self-typing python script that screen-records cleanly is the robust path.

## Round 3 — synthesis
Consensus reached:
1. **Real engine, scripted policy** — accepted by all. The metrics and the resolve/non-resolve
   are the engine's; the trajectory is fixed for reproducibility (RLE wins on determinism).
2. **Keep the failing band-aid in-engine** (PSRE's condition): the wrong tool must actually
   not resolve per `sim/engine.py`, asserted in code (`assert not ok`).
3. **Honest disclosure without watermark theater** (SMR/REV compromise): docstring +
   storyboard + narration all state it's a reproducible scripted demo over a real sim.
4. **No hard asciinema dependency** (DVO): script runs with plain `python3`; recorder produces
   a text transcript always, a `.cast` only if asciinema exists.
5. **Document the video blocker** (REV/DVO): we cannot record/encode video here; deliver the
   recipe + the exact commands so a human (or a CI with asciinema/agg) finishes it.
