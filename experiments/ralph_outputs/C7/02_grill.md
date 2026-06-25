# C7 — Grill (Ralph Loop): 5 personas, 3 rounds

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **AAAI** (AAAI Reviewer),
**RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial take

**SMR:** The design is sound: synthesis only ever sees TRAIN(simple) labels, and we test on a
held-out *family*. That's a genuine OOD generalization test, not a same-distribution holdout.
The metric I care about is the gap `acc(simple) - acc(cascade)`. But I want the hand-written
`is_safe` as the reference oracle — its gap tells us how much of the drop is irreducible
distribution shift versus synthesis overfitting.

**PSRE:** From an ops view, the only number that matters is **false-allow rate on cascade**.
Accuracy can look great while you let a single dangerous action (e.g. `scale_deployment` that
herds Spanner) through. Cascades are exactly where naive fixes worsen the incident. Report
false-allow separately and loudly; do not bury it in accuracy.

**AAAI:** Define "transfer gap" precisely and make it falsifiable. If you only report one number
you'll get desk-rejected. Also: is the label distribution comparable across families? If cascade
has a wildly different block/allow base rate, accuracy is not comparable — you need the confusion
matrix, not just accuracy.

**RLE:** Budget. The brief caps compute at ~15 min and the haiku operator is the bottleneck.
Eight LLM calls is fine. But seed determinism matters — set `seed=0` in `thompson_search` so the
result is reproducible. Also: what if the LLM is down? You need a graceful floor.

**DOL:** Do NOT edit `rex/harness_synth.py` — other Ralph workers import it concurrently. Make a
standalone script that imports the functions. And actually RUN it; a plan with no numbers is
worthless.

## Round 2 — react to another persona (genuine disagreement)

**PSRE → SMR:** I disagree that the hand-written `is_safe` is the right *reference* for the gap.
`is_safe` is data-driven over `forbidden_categories` which are loaded per-incident from specs — it
does NOT "generalize", it just *looks up* each incident's ruled-out causes. So its cascade accuracy
is near-perfect by construction. Using it as the ceiling makes the synthesized harness look
artificially bad. The honest reference is: does the *synthesized rule* recover the SAME general
pattern (`treats_forbidden_category==True → block`) that the hand-written Layer-1 encodes?

**SMR → PSRE:** Fair, and I'll concede half of it. `is_safe` isn't "learning," agreed. But it's
still the right *upper bound* to quote, precisely because it shows the task is solvable at ceiling —
the synthesized gap *relative to* that ceiling is the synthesis cost. I reject throwing the baseline
out; I accept your point that we must NOT call the baseline gap "generalization" — it's an oracle.

**AAAI → RLE:** "Set seed=0 and it's reproducible" is too glib. The haiku operator is *stochastic*
at temperature 0.4 and depends on a remote model that can change under you. Reproducibility of the
*search driver* is not reproducibility of the *result*. You must report the model id, the budget,
AND save the actual synthesized rule-set so the claim is auditable even if the model drifts.

**RLE → AAAI:** Disagree that this sinks reproducibility. We pin `MODEL` and `BUDGET`, save the
rule-set and node scores. The *interpreter* (`is_safe_synth`) is fully deterministic over saved
rules, so given the saved rule-set the entire evaluation is replayable offline. That's the
reproducibility that matters for the claim. I accept saving the rule-set; I reject the framing that
LLM stochasticity makes the experiment unscientific.

**DOL → PSRE:** You want false-allow front and center, but if synthesis fails (LLM down) the
seed-empty ruleset allows everything → false-allow rate ~1.0 on cascade, which would look like a
catastrophic transfer failure when really it's an infra blocker. We must distinguish "synthesis
produced a real rule that didn't transfer" from "synthesis never ran." I'll gate the report on
whether the best ruleset is non-empty.

## Round 3 — synthesis

Consensus:
1. Report the **full confusion matrix** per harness per family (accuracy alone is insufficient —
   AAAI, PSRE). Surface **false-allow count and rate** explicitly (PSRE).
2. Quote BOTH the synthesized gap and the hand-written gap, but label the hand-written one an
   **oracle/upper-bound**, NOT "generalization" (SMR↔PSRE compromise).
3. The headline claim is qualitative + quantitative: does the synthesized rule recover the general
   `treats_forbidden_category → block` pattern, and what is its cascade false-allow rate?
4. Pin MODEL + BUDGET + seed; **save the synthesized rule-set and node scores** for offline replay
   (RLE↔AAAI compromise).
5. Detect the "synthesis didn't run / empty ruleset" case and report it as a **blocker**, not a
   transfer failure (DOL).
6. Standalone script, imports core, edits nothing, and is actually executed (DOL).
