# A9 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take

**SMR:** This is a *label-quality* task, not a modeling task. The payoff is a clean
external regressor (human MTTR) we can correlate with agent difficulty. The single
biggest threat is label noise from invented numbers — I want every label sourced.

**PSRE:** MTTR is a slippery term. "Time to mitigate" (kill switch flipped) is not
"time to full recovery" (backfill done). Cloudflare WAF 2019 was mitigated in ~27
min but the writeup spans hours. We must pick and document one definition per row.

**AAAI:** For a paper claim ("agent difficulty tracks human MTTR"), n matters. If
only ~10 incidents have known MTTR, any correlation is underpowered. The deliverable
must report coverage and refuse to over-claim. A scatter with n=11 is suggestive, not
significant.

**RLE:** I need the labels keyed by the *exact* `incident_id` the sim/eval uses, or
the join silently drops rows. And I need a difficulty signal to correlate against —
pass@k or step-count per incident — which A9 doesn't own.

**DOL:** Half these titles are clearly synthetic ("Synthetic simple incident",
"SREGym", "(novel)"). Forcing an MTTR onto those is meaningless. Tag them
not_applicable, don't pollute the regression.

## Round 2 — react to another persona (genuine disagreement)

**AAAI → SMR:** I disagree with SMR's framing that this is "just labeling." The
*construct validity* is the whole ballgame. Real MTTR conflates org maturity, blast
radius, and detection lag — none of which the sim models. Correlating it with sim
difficulty risks a spurious result dressed up as insight. The label is fine; the
*interpretation* SMR implies is the danger.

**PSRE → DOL:** Pushback. DOL wants to drop synthetics entirely, but for the
*synthetic* incidents we actually have a ground-truth "ideal" resolution path length
in the YAML (`canonical_fix.steps`). That's a cleaner difficulty axis than noisy human
MTTR. So don't just discard them — they're the *control group*. They get
not_applicable for MTTR but stay in the dataset.

**RLE → AAAI:** I half-agree with AAAI on power but reject the defeatism. n=11 known +
9 real-unknown means the immediate win is *coverage reporting and a correlation
stub*, not a p-value. Ship the harness; let whoever owns scores backfill. Blocking on
significance is scope creep.

**SMR → PSRE:** Concede PSRE's MTTR-definition point fully — that was the gap in my R1
take. I'll add an explicit `mttr_basis` field (documented/approximate/unknown) and an
`mttr_minutes` that records the *primary documented impact window*, with the caveat in
notes. Disagree with going per-service though: postmortems rarely give per-service
recovery, so outage-level is the only honest granularity.

**DOL → RLE:** RLE assumes the difficulty score exists elsewhere. It may not, yet. So
the stub must be runnable *today* with only repo assets — i.e. fall back to a
structural proxy from the YAML (node count, cascade, buried-gun). Otherwise A9 ships a
script nobody can execute.

## Round 3 — synthesis

Consensus:
1. **No invented MTTR.** Real-with-known -> cited value + confidence; real-with-unknown
   -> null + reason; synthetic/benchmark/novel -> not_applicable.
2. **Explicit MTTR definition per row** via `mttr_basis` (documented/approximate/
   unknown) + `notes`; granularity is outage-level by necessity.
3. **Keep all 32 rows**, including synthetics as a labeled control group.
4. **Coverage over significance:** report n, coverage %, and drop-on-unknown; do not
   ship a p-value or over-claim causation (AAAI's construct-validity caveat goes in
   the critique).
5. **Stub runs on repo assets alone** via a structural proxy, but accepts an external
   `--scores` file for the real correlation when pass@k/step-count exists.
