# F8 · 05 Ouroboros — 3 self-critiques of the spec

## Engineer A — "the determinism is overstated"
Problem found: the spec calls the replay tier "byte-for-byte deterministic" but never
proves the judge is pure. `scoring.py:79 deterministic_judge` uses stemming/keyword
hits — *is it order-stable and free of set-iteration nondeterminism?* `_stems` returns
a `set` (`scoring.py:56`); if any code iterates that set and joins it, ordering could
vary across runs. **Fix**: weaken the claim to "deterministic given fixed inputs"
and have `verify_repro.py` actually re-grade the same record twice and assert equality,
rather than asserting determinism by fiat.

## Engineer B — "verify_repro hides failures by design"
Problem found: spec says PARTIAL/BLOCKED checks "never fail the run." That makes the
script green even when the repo is, in fact, not reproducible — a reviewer would call
this gaming. Also `check_committed` shells out to `git`, which fails silently outside a
git tree or in a worktree. **Fix**: (a) exit code stays 0 only for AVAILABLE/SEEDED
regressions, but print an explicit `WARN` line per PARTIAL/BLOCKED so they're visible
and counted; (b) guard `git` calls in try/except and report `UNKNOWN` instead of
crashing or false-passing.

## Engineer C — "the data story is internally inconsistent"
Problem found: 03 says the committed `.jsonl` has 197 rollouts / 3 models including
`kimi-k2p5`, but DATA.md advertises a Claude-only half + pending glm/minimax. The
checklist must not silently pick one; a reviewer reads DATA.md first and will distrust
the whole artifact on the mismatch. Also: is 197 the *final* dataset or a mid-merge
state? Over-claiming "dataset is complete" is a trap. **Fix**: add an explicit
"doc/data drift" item flagging that DATA.md is stale relative to the committed file,
report the *measured* counts (from a command, shown in 07), and mark the dataset
AVAILABLE-but-document-stale rather than a clean green.

## Filtered final spec (deltas applied)
1. Replace "byte-for-byte deterministic" → "deterministic given fixed inputs," and
   `verify_repro.py` empirically re-grades one record twice and asserts equality
   (new check `repro.replay_double_grade`).
2. `verify_repro.py`: PARTIAL/BLOCKED emit visible `WARN`, are tallied, and never
   silently pass; all `git` calls wrapped, degrade to `UNKNOWN`.
3. Add checklist item `data.doc_drift` = ⚠️ PARTIAL with the measured counts as evidence.
4. Everything else from 04 stands.
