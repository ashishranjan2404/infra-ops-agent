# Draft sign-off request message

> Send-ready draft. Channel-agnostic (works as email or Slack). Edit the bracketed
> deadline before sending. Do NOT send automatically — this is a coordination
> artifact for a human to dispatch.

---

**Subject:** Action needed — sign off your claims before SRE-Degrees submission

Hi Ashish, Wenji, Sylvie,

Before we submit, I need each of you to formally sign off on the paper's claims so
nothing ships that an author hasn't personally checked. I've built a one-page
sign-off sheet that pairs every major claim with its exact evidence pointer (file +
diagram) and the known caveats we already agreed on. It's grounded entirely in
`experiments/CLAIMS_EVIDENCE.md` — no new numbers.

**Sheet:** `experiments/ralph_outputs/F10/artifacts/signoff_sheet.md`

**What I need from each of you (≈15 min):**
1. Open the sheet. Edit ONLY your own column (Ashish / Wenji / Sylvie).
2. For each claim row, open the cited evidence file, then set your cell to one of:
   `APPROVED` · `APPROVED w/ comment: <text>` · `REJECTED: <text>`.
3. Pay special attention to the claim you're primary reviewer on (see the
   responsibility map at the bottom of the sheet).

**Two hard blockers we can't clear today — please action:**
- **Wenji:** Claim C2 (Fireball transfer) is *unreviewable* until the GRPO branch is
  pushed to the shared repo — the evidence isn't in the codebase yet. Please push it,
  then sign C2. Also: confirm whether RLVR ran *with or without the harness in-loop*
  (open question N2) — it changes how we read the fine-tuning results.
- **Everyone:** Claims N1/N2 are negative/incomplete results (Diagram 6 reward was
  FLAT, runs crashed). We're disclosing them, not claiming them — please confirm the
  disclosure wording is acceptable.

**Deadline:** [FILL IN — suggest 48h before submission].

When you're done, run `python3 check_signoff.py signoff_sheet.md` (or just ping me)
so I can see the cleared/blocked tally. A claim only ships when all three columns
read APPROVED.

Thanks,
[Your name]

---

## Per-author TL;DR (paste individually if needed)

- **Ashish:** You're primary reviewer on C1 (harness) and C3 (REx+SME). Confirm the
  2.8x lift and the "baselines too close" caveat are stated honestly.
- **Wenji:** Push the GRPO branch first (C2 is blocked without it), resolve the
  RLVR-harness question (N2), then sign C2 + N1/N2.
- **Sylvie:** You're primary reviewer on S4 — confirm the 4 v2 false-allows are
  genuinely unlearnable from an incident-semantics standpoint.
