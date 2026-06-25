# F15 — 10 Feedback for the next task

Source-of-truth trees can change *under you* mid-run: at plan time F6's `sections/*.tex` were empty,
but a concurrent worker filled all six by implementation time. The lesson that paid off was building
tooling that *reports* the state of its inputs (advisory exit + readiness verdict) instead of
hard-coding an assumption about them — the packager produced the right answer in both the empty and
populated states without edits. For any "package/submit/publish the artifact of another task" job:
(1) read the upstream tree at the moment you run, don't trust the plan-time snapshot; (2) make
correctness checks that mirror the real downstream system (here: arXiv runs AutoTeX, so `.bbl` not
`.bib` is the gate) rather than generic file-existence checks; (3) never fabricate the parts a human
must own (author identities, the actual upload), and turn those into explicit gated checklist items;
and (4) bake determinism in from the start (gzip mtime=0, sorted TarInfo) — it's cheap and makes the
artifact reproducible and reviewable.
