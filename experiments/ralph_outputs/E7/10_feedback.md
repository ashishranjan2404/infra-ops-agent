# E7 — 10 Feedback for the next task

The highest-leverage move was designing the canonical trajectory schema so its
field names line up 1:1 with what `rex/scoring.py` already consumes — that let an
adapted *game* episode flow into the project's real deterministic judge with zero
core edits, which is both the cleanest parallel-safe pattern AND the most
convincing demo (real import, not a mock). Lesson for next tasks: when bridging a
new data source into this repo, first read the *consumer's* signature
(`deterministic_judge(stated_cause, gold_root, red_herrings)`) and shape your
schema to it, rather than inventing a schema and writing glue later. Also: be
ruthless about the synthetic-vs-real boundary — the grill/ouroboros personas
correctly forced the docs to say "this proves plumbing, not transfer," which
keeps the deliverable honest and un-rejectable. The recurring blocker in this
sandbox is no-network/no-dataset; the right shape is always a runnable adapter +
fixture + protocol + named blocker, never fabricated numbers.
