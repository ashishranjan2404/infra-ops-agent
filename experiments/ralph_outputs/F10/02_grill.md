# F10 — 02 Grill (Ralph Loop, 5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer
(REV)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR:** A sign-off sheet is process, not science, but it's the right process. The
value is forcing each author to actually open the evidence file before approving.
Pair every claim with a file pointer and a number. Good.

**PSRE:** From an incident-review mindset this is a change-approval checklist. I want
a *primary reviewer of record* per claim — the person who owns that evidence — not
just three undifferentiated checkboxes. Diffusion of responsibility kills sign-offs.

**REV:** As a reviewer I don't see this sheet — so who is it for? It's for the
authors. Fine. But it must include the *negative* results too. If Diagram 6 reward
was flat, that has to be on the sheet as a disclosure the authors signed, otherwise
someone quietly drops it and a reviewer catches the inconsistency.

**RLE:** Make it machine-checkable. A markdown sheet humans edit will rot. Give me a
parser that tells me "0 cleared, 9 pending" so progress is mechanical, and that
fails loudly on malformed cells.

**DOL:** Ship a send-ready request message with an owner and a deadline. A sheet
nobody is asked to fill stays empty. And there must be one hard gate: a claim ships
only when all three columns are APPROVED — no partials slipping through.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**RLE → PSRE:** I disagree with PSRE's "primary reviewer" emphasis. If C2 has a
primary reviewer (Wenji), people will treat the other two sign-offs as rubber stamps
and not open the evidence. A primary reviewer *weakens* the three-way check. Keep
three equal sign-offs; the responsibility map is advisory at most.

**PSRE → RLE:** No. Without a named owner, *nobody* chases the missing evidence. C2's
GRPO branch isn't even in the repo. Three equal checkboxes means three people each
assume someone else will push it. Ownership is exactly what prevents that. Compromise:
keep three mandatory sign-offs AND name a primary reviewer who owns *unblocking*, not
who replaces the other two.

**REV → SMR:** SMR called this "process, not science." I push back — for a claims
paper, the sign-off *is* part of scientific integrity. The most likely failure mode
at AAAI is an over-claim the authors didn't individually vet (the 2.8x lift stated
without the "baselines too close" caveat). The sheet must carry the caveat *next to*
the number so you can't approve one without seeing the other.

**DOL → RLE:** RLE wants a parser that "fails loudly." Careful — if the validator
exits non-zero just because cells are PENDING, it'll block CI or scare people on day
one when everything is legitimately pending. PENDING is the correct initial state.
Only *malformed* should be an error. Make it a status report, not a gate.

**SMR → DOL:** DOL's hard gate "all three APPROVED or it doesn't ship" is too rigid
for C2. C2 is *unreviewable today* because its evidence isn't pushed. A blanket gate
just produces a permanently-red row. We need an explicit "blocked: evidence absent"
state distinct from "rejected," tracked in a blocker doc.

## Round 3 — synthesis

Consensus reached:
1. **Three mandatory, equal sign-offs** per claim (RLE's three-way check) **plus** an
   advisory primary-reviewer map that assigns *unblocking ownership* (PSRE's point) —
   not a replacement for the other two.
2. **Negative results N1/N2 are on the sheet** as disclosures requiring sign-off (REV).
3. **Caveat sits next to the number** in every row so over-claiming is visible (REV).
4. **Validator is a status report**, not a CI gate: PENDING is normal, only malformed
   rows error (DOL vs RLE resolved). It tallies cleared/partial/rejected/pending and
   checks evidence files exist.
5. **C2 is explicitly "blocked — evidence not in repo"**, documented in BLOCKER.md,
   not silently left red (SMR).
6. **Send-ready request message with owner + deadline placeholder** (DOL).
