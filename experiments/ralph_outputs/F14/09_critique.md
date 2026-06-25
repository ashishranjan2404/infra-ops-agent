# F14 — 09 Critique (honest)

## What's weak
1. **It's an outline, not a deck.** No actual slides, figures, or rendered visuals were
   produced — the figures referenced (`docs/curriculum_rewards.png`, the system diagram, a
   Grafana screenshot) exist in the repo but were not assembled into the talk. A reviewer of
   *this artifact* gets a script, not a presentation. That's within the task scope ("talk
   outline") but worth stating plainly.

2. **Timing is theoretical.** 15:00 is computed from a per-slide budget, not measured against a
   real spoken rehearsal. Real talks drift; three 1:15 result slides (7, 10, 12) are the most
   likely to overrun. The zero-buffer advisory flags this but doesn't solve it — a presenter
   should rehearse and pre-plan which slide to cut (slide 15, related work, is the cut candidate).

3. **The honest framing is a double-edged sword.** Leading with the ablation (REx lift mostly
   evaporates) is intellectually correct, but a less charitable reviewer could read the whole
   talk as "the flashy method didn't work; here's what's left." The outline tries to reframe
   this as relocated rigor, but the spoken delivery has to land that pivot or the talk feels
   deflationary. This is a presentation-skill risk the outline can only partially de-risk.

4. **Small-n verifier claim is still the soft underbelly.** Even scoped, "0.90 on 3 held-out
   incidents" is a thin generalization claim. A determined AAAI reviewer attacks here: "expand
   the held-out set or downgrade the claim." The outline pre-empts this verbally but can't add
   data it doesn't have.

## What a reviewer attacks
- "Your env band is 20–50% — is that because the task is hard, or because your LLM-judge is
  noisy?" The talk asserts the judge grades mechanism but doesn't show judge reliability.
- "You claim cascades are 'physically real' on GKE but most trajectories come from the sim —
  how much of your data is actually validated?" The two-tier contract slide answers this
  honestly but a skeptic will press the sim/real ratio.
- "If REx doesn't help under fair control, why is it in the title/system at all?" Fair; the
  outline keeps REx as the *vehicle* that exposes the env, not as a claimed win — must be said.

## What's missing
- No speaker-time contingency table (which slide to drop if at 11:00 you're only on slide 8).
- No explicit "anticipated questions" list beyond the backup slides.
- No accessibility/figure-readability notes (font size, colorblind-safe charts).

## Honest bottom line
The deliverable is a solid, grounded, reviewer-aware **outline** that correctly centers the
defensible contributions and refuses to overclaim. Its limits are exactly the limits of an
outline: it is not a rehearsed, rendered talk, and it cannot manufacture the larger held-out
verifier evaluation that would make the headline result bulletproof.
