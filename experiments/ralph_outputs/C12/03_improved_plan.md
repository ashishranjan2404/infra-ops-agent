# C12 — Step 3: Improved Plan (post-grill)

## What changed vs. 01_plan.md

1. **Reframed the central claim** from a vague "3 rules suffice (VC-style)" to a
   precise **combinatorial realizability theorem over the realized feature set**:
   > Over the finite set V of feature vectors realized by all loadable scenarios ×
   > candidate actions, the block/allow labelling is realizable by a disjunction of 3
   > conjunctive rule-schemas; therefore zero additional separating power is available
   > from a 4th schema (empirical risk is already 0). (Accepted: SMR, AAAI.)
   The PAC/worst-case generalization claim is explicitly DROPPED as out of scope.

2. **Honest rule-counting.** R3 is acknowledged to carry a *tool-indexed precondition
   table* (last-node / replica-cap / no-deploy). I count **3 schemas**, and a sidebar
   discloses that R3 expands to 3 tool-keyed conditions — so a skeptic can recount as
   "5 conjunctions" if they prefer; both numbers are reported. (Accepted: DOL.)

3. **Added a mandatory empirical witness step**: `verify_three_rules.py` enumerates the
   realized trap-action space across ALL scenarios, applies the 3-schema classifier,
   and reports misclassifications AND any feature-vector collision where one vector
   carries both a block and an allow label (which would *disprove* separability).
   (Accepted: AAAI, RLE.)

4. **Promoted the concurrency limit to a headline limitation.** The theorem covers
   single-action gating only; multi-action interaction hazards (two safe actions unsafe
   together) are provably outside any set of single-action rules and are named as
   Limit #1. (Accepted: PSRE.)

5. **Disclosed the `tool` categorical capacity.** The "6 features" includes a ~13-value
   categorical `tool`; the honesty section states the effective hypothesis class size
   so we don't undersell capacity. (Accepted: RLE.)

## Critiques rejected (with reasons)

- **AAAI's demand for a distributional/PAC theorem — REJECTED.** The harness never
  claims worst-case generalization; forcing a PAC bound would make the doc dishonest
  (we cannot bound an unknown incident distribution). We instead claim the weaker,
  *true* combinatorial result and label generalization as conjecture + held-out
  evidence. (SMR's counter accepted.)

- **PSRE's "R3 is genuinely one rule via mechanism unification" — PARTIALLY REJECTED.**
  The mechanism intuition is kept as motivation, but the honest *count* follows the
  interpreter's granularity (one rule per conjunction), per DOL. We do not claim R3 is
  atomically one rule.

## Final structure of the proof doc
1. Setup & notation (feature space, action space, label function).
2. Assumptions (A1–A5), stated up front.
3. The three rule-schemas (R1 category, R2 fault-masking, R3 precondition-exhausted).
4. Exhaustiveness lemma: every hazard label ∈ {A,B,C}.
5. Realizability theorem + proof (combinatorial, over realized set V).
6. Information-theoretic restatement: H(block | class) = 0 on V.
7. Why a 4th rule adds nothing (corollary).
8. Limits (concurrency, fixed-feature, distribution, adversarial substrate).
9. Honesty: this is an argument backed by an empirical witness, not a closed-form
   worst-case proof.
