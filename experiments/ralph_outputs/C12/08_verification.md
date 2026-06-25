# C12 — Step 8: Verification against success criteria

| Success criterion (from 01_plan) | Met? | Evidence |
|----------------------------------|------|----------|
| Proof doc states assumptions     | YES  | `three_rules_proof.md` §2, A1–A5 |
| States the theorem with quantifiers | YES | §4 Lemma 1 (proven), §5 Prop 2 (verified), over realized set V |
| Gives a proof where it is a proof | YES | Lemma 1 is a full enumeration proof of the 3-mechanism partition |
| Honest where it is an argument not a proof | YES | Abstract banner; §5, §7, §9 explicitly label Prop 2 empirical + the FAIL |
| Grounded in the ACTUAL rules     | YES  | Cites `is_safe`, `TOOL_TREATS`, `ground_truth`, `FEATURES`, `features` by name/line |
| Information-theoretic content    | YES  | §6: `I(y;R₄|c)=0`, `H(y|c)≈0` — 3 rules saturate Φ |
| ≥3 named limits                  | YES  | §9: concurrency, fixed-feature, realized-set, adversarial (4 limits) |
| Runnable witness artifact        | YES  | `verify_three_rules.py` runs, py-syntax OK, real numbers in 07 |

## Are the outputs REAL (not placeholder)?
- The verifier executed against 42 real scenarios (580 examples) and produced
  reproducible numbers (n=580, mismatches=39, feature-subset 529/531). Not fabricated.
- The proof's claims are tied to those exact numbers; the negative result (FAIL on full
  corpus) is reported rather than hidden, which is the strongest evidence the outputs
  are real.
- No shared core file was modified (git shows only `?? experiments/ralph_outputs/C12/`).

## Key honesty check
The task asked for a "formal proof or argument." We deliver a **proof of the part that
is provable** (3 mechanism classes saturate the fixed feature space) and an **honest
empirical argument + named failure modes** for the global claim. We did NOT overclaim a
universal sufficiency theorem — the witness showed it would be false.
