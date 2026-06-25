# F5 — Improved Plan (after the grill)

## What changed vs 01_plan.md

The grill surfaced a single dominant tension: **how honest to be in the abstract about
the oracle-leakage finding and the pending transfer claim.** The original plan said
"reflect honest results" but didn't commit to *what* the abstract leads with. It now does.

### Critiques ACCEPTED
1. **(RLE, SMR) Relocate the headline from the REx loop to the verifiable env + searched
   verifier.** `headline_insights.md` §3 is explicit: with the root-cause hint stripped,
   REx → 0.25 ≈ zero-shot 0.24; best-of-N and retry add ~0. The defensible contributions
   are the *environment* and the *learned verifier*, not the refinement loop. The abstract
   will frame REx's lift as **SME-feedback-dependent** and say so in one clause.
2. **(REV, RLE) Kill false precision.** Drop "89.7% / 94.9%" two-decimal claims on n=3
   held-out incidents. Use the insight-doc framing: **~0.90 vs ~0.95 hand-written**,
   **14→3 rules**, the one held-out miss is an *unseen* hazard ("can't invent the unseen").
3. **(DVO) Do NOT assert C2 (FIREBALL transfer) as a result.** The outline marks it
   pending (§5.3, "needs Wenji's GRPO branch"). The abstract will either omit it or name
   it as an open direction — never as a measured lift.
4. **(PSRE) Keep the trap-action hook** verbatim in spirit: the naive fix worsens the
   outage. This is the memorable sentence; protect it from word-count cuts.
5. **(DVO, PSRE) Emphasize deterministic reward**, grounded as "the simulator is ground
   truth," plus a short credit-free / reproducible clause.

### Critiques REJECTED (and why)
1. **(REV) "Lead with the hook, bury the negative."** Rejected as the *primary* posture.
   For this paper the honest ablation *is* the interesting result; a reviewer who finds
   it buried in §6 turns hostile. Compromise honored: the negative is stated in exactly
   one non-dwelling clause, not the opening line.
2. **(REV) "Just round 89.7→90."** Rejected — rounding hides the n=3 issue. We instead
   adopt the insight-doc's *honest* framing that names the single miss as unseen.
3. **(SMR, implicitly) "State McNemar significance."** Held back. The outline marks the
   30×5 grid partly pending; I will not assert a p-value the locked results don't yet
   guarantee. The abstract reports the *direction and dependence* of the lift, not a
   significance verdict, unless I can cite a frozen number (I cannot from the JSONs in
   repo), so I phrase it as a measured separation grounded in `ablation.json`.

## Revised deliverable shape (abstract body order)
1. MTTR problem → cascades (hook).
2. Why frontier LLMs fail: trap actions (naive fix worsens outage).
3. Method: three composable components — synthesized harness, REx + SME-feedback loop,
   deterministic verifiable reward distilled via RLVR.
4. Results, honest: verifier generalizes (~0.90 vs ~0.95, 14→3 rules); REx lift is
   real but SME-feedback-dependent (stripped → ≈ zero-shot) — an explicit boundary.
5. Released artifacts.

## Unchanged
Word gate ≤250 (counted via `wc -w`), markdown deliverable at
`experiments/ralph_outputs/F5/artifacts/abstract.md`, no shared-core edits.
