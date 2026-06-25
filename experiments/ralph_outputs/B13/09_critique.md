# B13 — 09 Critique (honest)

## The central honest result: the headline number is BLOCKED
The scientifically interesting quantity — does the deterministic judge agree with human
SREs (criterion validity), and do humans agree with each other (task quality) — is NOT
produced, because there are no human labels. What I delivered is the *apparatus*: a tested
IAA library, a primed/blinded worksheet over 126 real episodes, and a written protocol.
A reviewer is entitled to say "you measured nothing about validity." That is correct. The
defense is that B13 is, by its own framing ("if humans relabel"), gated on a human input we
don't have, and a correct primed apparatus is the most that's truthfully deliverable.

## Where a reviewer attacks

1. **Machine-vs-machine kappa=1.0 is vacuous.** Proving a deterministic function is
   deterministic. Mitigated by the second-grader baseline (0.917), but even that compares
   two graders we built, not the judge against an independent standard. It bounds
   *internal* consistency, says nothing about *correctness*.

2. **The worksheet panel is too easy.** Gold-paraphrase and generic-non-answer rows are
   near-trivially labelled; human kappa on them would be inflated and uninformative about
   the judge's borderline failures (exactly the cases that perturb the 30% reward term).
   The substantive study needs real model-generated stated_causes from eval traces mixed
   in (documented in 04 §C / 05-E2) — not done here to keep the artifact deterministic and
   LLM-free.

3. **Synthetic ground truth.** "Human agreement with the judge" on synthetic incidents
   partly measures agreement with the scenario AUTHOR's gold, not with reality. On a real
   page humans might dispute the gold itself. So even completed human IAA here would be a
   weaker claim than IAA on real incidents.

4. **Krippendorff's alpha unverified externally.** Validated only against hand-computed
   perfect/missing/partial cases, not a reference library. Low but non-zero risk of a
   subtle weighting bug in the coincidence-matrix path.

5. **n and panel coverage.** 126 episodes, 42 scenarios, 3 fixed candidate types. No
   per-family balancing or power analysis for the eventual human study.

## What's weak / missing
- No real model-trace episodes (the contestable ones).
- No annotator recruitment, no adjudication artifacts (blocked).
- No power/sample-size calc for the planned human study.
- mechanism-family error breakdown is *enabled* (provenance/scenario columns) but not
  computed (needs human labels).

## What's genuinely solid
- The IAA library is correct on its tested surface and reusable beyond this task.
- The worksheet is built from the REAL judge over REAL scenarios — no fabrication.
- The blocker is stated plainly, not papered over with a fake human number.
- The protocol is concrete enough that the next worker can run the human study unchanged.
