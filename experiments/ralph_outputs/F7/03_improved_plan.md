# F7 — 03 Improved Plan (post-grill)

## What changed vs. 01_plan.md

1. **Severity now has two axes, not one.** Each attack gets `probability` (how likely a reviewer
   raises it) AND `depth` (how fatal if true). The grill (REV vs PSRE) showed these dissociate:
   "small N" is high-probability/medium-depth; "construct validity" is medium-probability/
   high-depth. A single FATAL/SERIOUS tag would have hidden this. **Accepted (REV+PSRE).**

2. **Added explicit callouts:** "Highest-probability rejection" (small N / no CI / no seeds) and
   "Highest-depth rejection" (the environment is a caricature of incident response). The doc
   leads with these. **Accepted (synthesis pt 1).**

3. **Flat RFT reframed from "a weakness to defend" to "a concession to make up front."** The
   contribution is scoped as *environment + reward + inference-time REx*; RFT is presented as an
   honest negative/ongoing result (0.522 → 0.491). **Accepted (RLE).**

4. **The 0.86 = (4×1.0+0.30)/5 fixed point is listed AS AN ATTACK in its ugliest form first,**
   then defended with the escalation-holds evidence — not pre-spun as a feature. **Accepted
   (SMR over RLE).** I rejected RLE's "don't list it, it's a defense" because a reviewer computes
   it themselves; disclosure dominates decoration.

5. **The synthetic-data attack is sharpened to "reconstruction fidelity / answer leakage,"** per
   DOL: the strongest honest version is "your reconstruction of public post-mortems may encode
   the very root cause you then reward," not "it's all fake." **Accepted (DOL).**

6. **Added DOL's two cheap-but-real attacks:** (a) circular LLM-judge (grader is a frozen LLM of
   the same family), (b) gateway models not pinned → non-reproducible table. **Accepted (DOL).**

## What I rejected and why
- **RLE's "omit the 0.86 fixed-point attack."** Rejected: a competent reviewer derives it
  unprompted; pre-empting it is strictly safer (SMR's point). We keep it as a top attack.
- **REV's implicit "N is the only attack that matters."** Rejected as framing: we keep N as the
  highest-*probability* attack but explicitly note it is *survivable* (add incidents + CIs),
  whereas construct validity may not be. Don't let the easy attack crowd out the deep one.
- **PSRE's "construct validity is near-fatal, full stop."** Partially rejected: DOL's
  reconstruction corpus blunts the "it's all invented" version. We keep the depth ranking but
  scope the attack to fidelity, not fabrication.

## Final deliverable shape
`rebuttal_anticipation.md` with: (i) two top-line callouts, (ii) 10 attacks each =
steelman + honest response + probability + depth + closing evidence, (iii) concession ledger,
(iv) "what would actually sink the paper." Plus `attacks.json` + `validate_attacks.py`.
