# F7 — 09 Critique (honest)

## What's weak about this deliverable

1. **It's a doc, not an experiment.** The strongest rebuttal is a result, not a paragraph. This
   task produces the *map* of attacks and honest responses, but every "Closing evidence" line is
   a promise (run CIs, do a human-SRE agreement study, add no-clean-fix incidents) — none are
   executed here. A reviewer of *this artifact* would say "fine, now go do A1–A10's closing
   evidence." That's correct; this is preparation, not proof.

2. **The validator guards form, not substance.** It enforces structure, label presence, a
   120-char floor, and the A6 arithmetic — all of which a sufficiently lazy author could satisfy
   with verbose filler. There is no automated check that a steelman is *actually* the strongest
   version of the attack or that a response doesn't overclaim. I mitigated this by hand (the
   grill + ouroboros forced genuine adversarial content), but it's a real limitation of the test.

3. **Possible self-serving framing on A6.** I argue the 0.86 fixed point is "correct ceiling
   behavior." A hostile reviewer can still read identical convergence across 5 models as metric
   saturation regardless of the escalation story. The honest response concedes this and proposes
   raising the ceiling — but the doc can't *prove* the escalation interpretation is the right one
   without the harder-tier experiment. The defense is plausible, not settled.

4. **Attack selection is mine.** I chose 10 attacks; a real PC samples reviewers I didn't model
   (e.g. an ethics/safety reviewer on "automating incident response is dangerous," or a systems
   reviewer on the GKE Tier-B's representativeness). The set is grounded and covers the mandated
   weaknesses, but it is not exhaustive.

5. **No external calibration.** I didn't run `claude-notebook` or pull prior reviews of similar
   benchmark papers to calibrate which attacks *actually* show up most. The probability tags are
   informed judgment, not data.

## What a reviewer attacks about F7 itself
- "Your rebuttal doc just restates your own limitations section." Partial truth — the value-add
  is the *steelman + severity ranking + what-would-sink-it triage*, which a limitations section
  usually lacks, but the overlap is real.
- "Where's the evidence the mitigations work?" — Valid; out of scope for this task, flagged.

## Honest bottom line
Deliverable is real, validated, and well-grounded in the project's actual numbers, and it
correctly identifies the two existential risks (construct validity + answer-leakage/judge
circularity compounding). It is genuinely useful as rebuttal prep. It is *not* a substitute for
running A1/A2/A8's closing experiments, and it should not be cited as if the attacks are
*answered* — only as if they are *anticipated and triaged*.
