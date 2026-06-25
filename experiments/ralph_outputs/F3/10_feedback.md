# F3 — Feedback for the next task

For authoring tasks that ride on a project's thesis, the highest-leverage move is to pin every
quantitative claim to a `file:line` and write a tiny stdlib validator that greps the exact
(Unicode-faithful) value strings back out of the source docs — it caught a real mis-citation
here (the reward formula is at `ARCHITECTURE.md:75`, not README) that I'd otherwise have
shipped. Two source-grounding gotchas to carry forward: (1) the canonical numbers live in
`ARCHITECTURE.md` (REx table, 0.86 = `(4×1.0+0.30)/5` ceiling, curriculum 0.19–0.42 → 0.59–0.71,
haiku+REx 0.68 > opus 0.42) and the trust-tier/"earning trust" language lives in `README.md:26,77-79`;
(2) copy value substrings *exactly*, Unicode middots/minus included, or the check false-fails.
Metaphor honesty matters: the "graduation" frame is strong on trust tiers, the uncrammable
reward, and escalation-as-passing, but *revocation/demotion is designed-not-automated* — say
that aloud rather than letting the metaphor overreach. A later task could make this section
land harder by demonstrating an actual tool demotion.
