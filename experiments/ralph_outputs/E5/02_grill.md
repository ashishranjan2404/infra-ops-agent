# E5 — Ralph Loop Grill (5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (AAAI)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR:** A transfer/generalization test is only meaningful if the test set is provably
disjoint from training. A8 already did the hard part with a tiered novelty guard. Good
— reuse it, don't re-derive. The metric must be zero-shot (no in-context refinement)
or you're measuring search, not transfer.

**PSRE:** From an ops view, "novel" should mean a mechanism the policy hasn't been
drilled on, not just a renamed company. The A8 split includes *failure_class* reuse
flags (tier3). If the eval silently includes incidents whose failure_class was in
training, you're overstating novelty. Surface that flag.

**AAAI:** Where's the baseline? A single number for Fireball with no reference is
unreviewable. You need at least a floor (random/empty), a ceiling (oracle), and one
real competing policy. And report a CI — n=10 incidents × few seeds is a small sample;
a bare point estimate invites overclaiming.

**RLE:** Determinism. If the diagnosis judge is an LLM, your reward has sampling noise
and the transfer delta is unfalsifiable. Use the P0 deterministic judge. Also: what is
"Fireball"? If it's a checkpoint that doesn't exist in this repo's roster, the honest
move is to ship the harness and mark it blocked.

**DOL:** Parallel safety. Many Ralph workers run at once. Do NOT edit `rex/*.py` or the
registry. Import the frozen core, write only under `E5/`. And make the run resumable or
at least cheap enough that a flaky gateway doesn't wreck it.

## Round 2 — react to another persona by name (genuine disagreement)

**RLE → AAAI:** I disagree with the implied "oracle is enough of a ceiling." Oracle here
is the gold fix + gold root — it will score ~1.0 by construction. That proves the
harness can *award* a pass, but it's a trivial ceiling, not evidence the task has signal.
The real ceiling question is the *baseline-vs-Fireball spread*, and since Fireball is
blocked, we can't claim transfer at all. Be blunt about that in the writeup.

**AAAI → RLE:** Partially fair, but the oracle ceiling is not trivial — it's a *floor on
the floor check*. If oracle does NOT hit 1.0 on a novel incident, the incident is
mis-specified (unreachable gold), and the whole pass@1 for that incident is garbage. So
the oracle control is load-bearing for *data validity*, even if it's a weak ceiling for
*model quality*. Keep it.

**PSRE → SMR:** You said "reuse A8, don't re-derive." I push back on reusing it
*blindly*. A8's "novel" family is curated cascades (Facebook BGP, Knight Capital). Those
are great, but only 8 are held-out novel-family; to reach 10 you back-fill with held-out
*simple* incidents (redis flush, disk fill). Those are easy and will inflate pass@1.
The writeup must disclose the family mix, or the transfer number looks better than it is.

**SMR → PSRE:** Agreed on disclosure, disagree on "inflate." Mixing simple+novel is fine
*if reported per-family*; transfer to easy mechanisms is still transfer. The error would
be reporting one blended pass@1 with no family breakdown. So: keep the set at 10 for the
brief, but record family per incident and never collapse to a single hero number without
the breakdown.

**DOL → RLE:** Your "ship blocked" stance is right but incomplete. A blocked Fireball
with *no baseline numbers* is a non-deliverable. Even if Fireball is dead, the harness
must produce REAL baseline numbers (glm-5p2 is reachable on Fireworks) so the artifact
is independently useful the moment Fireball lands.

## Round 3 — synthesis

Consensus:
1. **Reuse A8** held-out set; select 10 (novel-family first, back-fill simple), assert
   each is a loadable rex scenario, and **record family + failure_class-reuse per
   incident** (PSRE/SMR).
2. **Deterministic P0 judge**, zero-shot, binary pass at 0.8, **pass@1 + Wilson CI +
   std** (RLE/AAAI).
3. **Controls are mandatory:** `empty` (floor must be 0) and `oracle` (ceiling must be
   1 = data-validity check) (AAAI/RLE).
4. **Run real baselines** (glm-5p2 reachable) so the artifact stands alone; record any
   unreachable policy as `blocked` with the reason, never dropped (DOL).
5. **Fireball = blocked**, stated plainly with the exact cause; no fabricated transfer
   delta (RLE/AAAI/DOL).
6. **No core edits**, all outputs under `E5/` (DOL).
