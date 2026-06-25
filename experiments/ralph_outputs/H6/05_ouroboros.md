# H6 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "Edge-case hunter"
**Problems found:**
1. **Silent-success on empty glob.** If `scenarios/cidg/` is moved/renamed, a naive validator
   would loop over `[]` and exit 0 — a false green. → FIXED: no-match is a hard exit 2.
2. **`validate()` itself raising.** The spec validator could throw (e.g. malformed nested dict)
   and bypass the schema-error path. → FIXED: stage 2 wrapped; a raise is classed `schema`.
3. **Path duplication.** Overlapping globs (`cidg/*` and an abs repeat) could double-count a
   scenario. → FIXED: `resolve_paths` de-dups on absolute path.

## Engineer B — "Semantics skeptic"
**Problems found:**
1. **Green ≠ correct.** `apply_fix` passing only means the action didn't crash, not that it
   resolved. A reader could mistake H6 for proof the scenario is solvable. → MITIGATED: stage is
   explicitly documented as a crash check; A16 named as the efficacy layer. Not a code bug, a
   framing risk — addressed in docs/comments, not by adding a flaky resolve assertion to CI.
2. **Over-broad `except Exception`.** Could swallow a `KeyboardInterrupt`-adjacent or a genuinely
   informative error. → ACCEPTED RISK, bounded: we catch `Exception` (not `BaseException`, so
   Ctrl-C/SystemExit pass through) and record type+message+last-3-traceback-lines, so nothing is
   truly silent.
3. **`sustain_ticks` default.** If a scenario has zero SLOs, `max(default=3)` runs 3 ticks — fine,
   but worth asserting SLOs exist. → Already covered: `validate()` flags "no SLO defined" at the
   schema stage, so a zero-SLO scenario fails earlier and never reaches settle.

## Engineer C — "CI/ops pragmatist"
**Problems found:**
1. **Hidden env requirements.** If the validator needed `PYTHONPATH` or a venv it'd be useless in
   CI. → FIXED: script self-inserts REPO on `sys.path`; stdlib + pyyaml only; `ci_check.sh` cd's to
   repo root and needs no env.
2. **No machine-readable artifact.** Humans read stdout, pipelines parse JSON. → FIXED: `--json`
   writes a structured report with per-stage failure counts; wrapper always emits it.
3. **Exit-2 vs exit-1 conflation.** Some CIs treat any nonzero the same, but distinguishing
   "config/harness broken" (2) from "a scenario is broken" (1) speeds triage. → KEPT distinct and
   self-tested.

## Final filtered spec (after the 3 passes)
The §04 spec stands, with these confirmations baked in: no-match→2, validate-raise→schema,
de-dup paths, `Exception`-not-`BaseException`, JSON artifact + per-stage counts, and explicit
documentation that `apply_fix` is a crash check (A16 owns efficacy). No new code paths were
needed beyond what these fixes already imply; all are present in the implementation.
