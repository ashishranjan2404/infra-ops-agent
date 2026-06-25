# B13 — 02 Grill (Ralph Loop, 5 personas, 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take

**SMR.** IAA on a deterministic judge is conceptually odd. kappa(judge, judge)=1.0 by
construction. The publishable claim is *criterion validity*: does the judge agree with
expert humans? So the worksheet is the real artifact; the machine baseline is a smoke
test. Make sure the worksheet samples episodes that are actually CONTESTABLE (paraphrased
gold, ambiguous herrings), not just trivially-correct/trivially-wrong, or human kappa
will be inflated.

**PSRE.** As the human labeler, I need the GOLD root and the red herrings in front of me,
plus the original alert/symptom prompt — otherwise I'm guessing. Two SREs will disagree
on borderline mechanism wording ("cert expiry" vs "TLS handshake failure"). That
disagreement is the signal we want to measure. Ship me the incident context, not just
the stated_cause string.

**AAAI.** If you report human-vs-machine agreement you MUST report human-vs-human first,
or I can't tell whether low agreement is a bad judge or a bad task. Also: blinding. If the
labeler sees `machine_label`, your IAA is contaminated. State the blinding protocol
explicitly and ship a copy with that column removed.

**RLE.** Practically: the judge feeds a 30% reward term. What I care about is whether
judge errors are *biased* (systematically over/under-crediting a mechanism family), not
just raw kappa. Add per-scenario / per-family error breakdown to the protocol so a low
kappa is actionable for reward de-noising.

**DOL.** Zero new dependencies, must run on the repo's Python 3.13, must not touch shared
core files (parallel workers). A CSV humans can open in any spreadsheet. Don't build a
labeling web app — overkill for n in the low hundreds.

## Round 2 — react to another persona (genuine disagreement)

**RLE -> AAAI.** I disagree that human-vs-human is mandatory *for this deliverable*. We
have ZERO human labels and no annotator budget this week. Demanding the full h-vs-h panel
before shipping anything means we ship nothing. Better: ship the protocol that REQUIRES
h-vs-h and the machinery to compute it, and mark human labeling as the blocker. The
library already supports >=2 raters precisely so h-vs-h drops in later.

**AAAI -> RLE.** Fine, but then don't dress up machine-vs-machine kappa=1.0 as a result.
That number is vacuous; it only proves the function is deterministic, which we already
knew. If you must show a machine baseline, show two DIFFERENT graders disagreeing — that
at least exercises the metric on real labels and gives a number a reviewer can't dismiss
as tautological.

**SMR -> PSRE.** Disagree slightly: don't hand the labeler the gold root *as the answer
key* during labeling — that biases them toward rubber-stamping. They should see the
incident PROMPT + the stated_cause and judge it cold, the way the judge nominally does.
The gold/herrings belong in the adjudication phase, not the blind-labeling phase.

**PSRE -> SMR.** Pushback: an SRE without the gold mechanism can't reliably know the
"true" root for a synthetic incident they didn't design — these aren't real pages they
investigated. For SYNTHETIC scenarios the gold IS the ground truth. So I keep the gold
visible but blind only the `machine_label`. We're measuring agreement with the judge's
*decision*, not re-deriving ground truth from scratch.

**DOL -> RLE.** Per-family error breakdown is good but that's an analysis layer on top of
labels we don't have yet. For B13 just make sure the CSV carries `scenario` + a
`provenance` tag (gold/herring/generic) so that breakdown is a trivial groupby later.
Agreed — added `provenance` column.

## Round 3 — synthesis

Consensus:
- The headline deliverable is the **protocol + machinery + primed worksheet**, NOT a
  human IAA number (blocked, honestly documented).
- Machine baseline = (a) idempotence check kappa=1.0 AND (b) judge-vs-second-grader kappa
  on real labels, explicitly framed as a smoke test not a validity result (AAAI's point
  accepted).
- Worksheet carries: incident context is implicitly the gold_root + red_herrings +
  stated_cause; blinding = ship a copy with `machine_label` hidden (AAAI accepted).
  We keep gold visible for synthetic ground truth (PSRE/SMR resolved -> gold stays,
  machine_label is what's blinded).
- `provenance` column added for later per-family error analysis (RLE/DOL).
- Library supports >=2 raters / missing data so h-vs-h and h-vs-machine drop in unchanged
  when labels arrive (RLE accepted).
- Zero deps, CSV-based, no shared-core edits (DOL accepted).
