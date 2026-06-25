# A16 — Ouroboros (3 self-critiques of the spec)

## Engineer A — correctness of the resolution check
**Problem found**: My first instinct was to read `_slo_ok` directly and AND it
with `root_cleared` myself. That duplicates engine logic and can drift. Also
`_slo_ok` is a private helper. **Fix**: call the public `is_resolved(world)`
verbatim as the single source of truth; only record `root_cleared` separately
as a diagnostic. Applied in `validate_one`.

**Problem found**: Without checking the pre-fix state I can't distinguish "fix
worked" from "incident never bit." A scenario whose fault doesn't reduce the SLO
would trivially 'pass'. **Fix**: record `fault_active_at_t0 = not is_resolved(world)`
before applying the fix, so a vacuous pass is visible in the report.

## Engineer B — robustness / blast radius
**Problem found**: A single malformed YAML or an unmodeled SLO metric raising
KeyError would abort the whole run, losing all other results. **Fix**: wrap each
scenario in try/except, record `status:"error"` + message, continue. Verified:
the run completed all 54 even with 3 KeyErrors.

**Problem found**: Hardcoding the 42 count (from the task title) would mislabel
the run as parallel workers add files. **Fix**: glob at run time, report actual
`total`. (Run-time count was 54.)

**Over-engineering check**: I considered modeling `persistent`/`reset_by`
hysteresis inside the validator to "complete" those scenarios. Rejected — that
re-implements engine physics in a test harness, which is exactly the kind of
shadow logic that hides real engine gaps. Note the gap, don't simulate it.

## Engineer C — reporting honesty / reviewer attack surface
**Problem found**: If I only printed pass/fail counts, a reviewer can't tell a
wrong-target authoring bug (`fail`) from an unmodeled-metric engine gap (`error`).
**Fix**: distinct `fail` vs `error` statuses, plus per-record `error` string and
`fix_steps` so the wrong target is visible in the artifact itself.

**Problem found**: The summary should make the central question answerable at a
glance: "which scenarios promise fix_resolves but don't deliver?" **Fix**: added
`broken_fix_resolves_promises` list to the summary.

## Final filtered spec deltas
- Use `is_resolved` as the only resolution oracle (Eng A).
- Record `fault_active_at_t0` to catch vacuous passes (Eng A).
- Per-file try/except, glob count, no hysteresis modeling (Eng B).
- Distinct fail/error + `broken_fix_resolves_promises` summary (Eng C).
All four deltas are present in `artifacts/validate_scenarios.py`.
