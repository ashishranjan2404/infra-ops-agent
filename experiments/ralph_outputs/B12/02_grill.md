# 02 — Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DevOps** DevOps Lead.

## Round 1 — initial takes

**SMR:** Per-incident pass@k is the right granularity — family-averages hide bimodality.
But "unsolvable" must mean *under the tested policies/budget*, not "unsolvable in principle."
A label collision there is the headline risk.

**PSRE:** From an ops view this is a triage map: which incident classes our auto-remediator
will silently fail. I want the unsolvable list front-and-center, not buried in a wide table.

**AAAI:** With only n=3 reps (A1), pass@1==0 is NOT strong evidence of unsolvability — that's
a 3-sample point estimate. You need a CI or at least to disclose n. Flagging "unsolvable" off
3 zeros is a reviewer red flag.

**RLE:** I care about training signal. The useful cut is incidents where *some* condition
solves it but zero_shot doesn't — those are the learnable-but-hard ones. Pure "best p@1==1"
collapses that. Keep per-condition columns, don't only emit the flag.

**DevOps:** Make it a single reproducible command with explicit input paths. No hidden globbing
of whatever JSON happens to be lying around — that breaks in CI.

## Round 2 — react to another persona (genuine disagreement)

**SMR → AAAI:** I disagree that n=3 kills the flag. "Unsolvable" defined as *best pass@1 across
5 conditions × n reps == 0* is an operational definition, not a population claim. For A1 that's
0/15 effective samples per incident (3 reps × 5 conditions). 0/15 is not nothing. The fix is
wording, not deletion.

**AAAI → SMR:** 0/15 conflates conditions that share a proposer and are positively correlated —
they are NOT 15 independent Bernoulli trials. So your "0/15" CI is overconfident. I'll concede
the *flag* is fine as an operational triage label IF you stop implying statistical impossibility
and report raw n per cell.

**RLE → DevOps:** Reproducibility is fine but you're under-asking. A single command that only
prints a table is useless for the next loop. It must emit JSON so downstream tasks (curriculum
reweighting) can consume the unsolvable set programmatically.

**PSRE → RLE:** Hard disagree on hiding the flag behind per-condition columns. On call I don't
read a 16-column table — I read "these 3 incidents always fail." Both must exist: machine JSON
with full per-condition detail AND a short human unsolvable list. Don't force a choice.

**DevOps → SMR:** Your "best across conditions" flag can mask a regression where the GOOD
condition (rex) degrades but best_of_n masks it. Fine for solvability triage, but the JSON must
keep every condition so we can detect that separately.

## Round 3 — synthesis
Consensus:
1. Keep the flag, but define it **operationally** ("no tested condition passes a single sample")
   and **always report n** per cell — drop any language implying statistical impossibility (AAAI/SMR).
2. Emit BOTH machine JSON (full per-condition pass@1/pass@k) and a human Markdown with a short,
   prominent unsolvable list + by-family rollup (PSRE/RLE).
3. Keep per-condition columns so learnable-but-hard incidents and per-condition regressions stay
   visible (RLE/DevOps).
4. Explicit input paths, single reproducible command, 0-error run (DevOps).
5. Never pool reps across models; one row per (model, incident) (AAAI).
