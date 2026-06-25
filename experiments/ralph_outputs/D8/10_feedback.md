# D8 — 10 Feedback for the next task

When a task is gated on data/infra you don't have, the highest-value move is to
build the *seam* the missing piece will plug into — a defensive ingest adapter, a
fail-closed config, and a synthetic fixture + unit test that exercise every branch
— and to make the blocker impossible to miss (state it in the adapter, the config,
07, 09, and SUMMARY). Two pitfalls worth flagging forward: (1) any field named
`reward`/`score` in a scaffold reads as a fabricated result unless you explicitly
redefine its semantics (here: a data-quality loss weight, not a game score) — name
and document it before a reviewer assumes the worst; and (2) keep adapters as pure
transforms but be honest that guards living only in the config (like
`min_examples_for_real_run`) are a seam a careless caller can step over. Build the
harness, refuse to fake the numbers, and record the acceptance bar (multi-seed +
CI on a pre-registered split) so the eventual real run is trustworthy.
