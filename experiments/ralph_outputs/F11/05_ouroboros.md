# F11 — 05 Ouroboros: self-critique as 3 engineers

## Engineer 1 — Reproducibility pedant
**Problems found:**
- P1.1: Spec says "Reproduced = within paper's Wilson CI" but the paper's CI is not yet a frozen
  number in this repo. If the appendix hardcodes a number we'd be fabricating. **Fix:** appendix
  states the tolerance *rule* and the JSON key to read, and marks the paper figure as
  `<from camera-ready Table X>` placeholder — never invents a value.
- P1.2: `smoke_ae.sh` computes repo root via relative path; if the evaluator copies the script out
  of the tree it breaks. **Fix:** resolve root from the script's own location AND allow a
  `REX_REPO` env override; document it.
- P1.3: floor_check inside smoke runs on a *2-per-family* subset — if a leaky scenario is outside
  that subset the smoke passes falsely. **Fix:** run floor_check over the *full* registered set in
  the smoke (it's cheap — no LLM), not a subset.

## Engineer 2 — AAAI AE chair
**Problems found:**
- P2.1: The check-list must state **disk** and **setup/run time** estimates or AE chairs bounce it.
  Spec mentions them in the schema but the appendix draft must actually fill them. **Fix:** fill:
  disk <50 MB, setup ~2 min, Tier-A run <1 min, Tier-B run hours + API cost.
- P2.2: License unstated. AE *Available* requires a clear license. **Fix:** appendix points to repo
  LICENSE; if absent, flag as a pre-submission TODO rather than asserting one.
- P2.3: "GitHub clone main" is not archival. **Fix:** appendix's How-to-access leads with the
  pinned tag + Zenodo-DOI procedure, mentions `main` only as the dev pointer.

## Engineer 3 — Adversarial evaluator (tries to fail the artifact)
**Problems found:**
- P3.1: If `test_badge_map.py` only checks files exist, a command could still be wrong (bad flag).
  **Fix:** also assert the online command string contains the real module path AND at least one
  real flag (`--conditions`), and that the offline command names a real test file. (Cheap string
  checks; full execution of Tier B needs $.)
- P3.2: An evaluator with no API key must still reach a verdict. If the appendix only earns
  Functional offline, the evaluator can't even *attempt* Reproduced — appendix must say that's
  expected and that Reproduced requires the maintainer-provided key or the evaluator's own gateway.
  **Fix:** explicit "credential-free evaluators stop at Functional; this is by design" note.
- P3.3: LICENSE check — does the repo even have one? Must verify, not assume. **Fix:** check in 07.

## Final filtered spec (deltas applied)
- smoke_ae.sh: root via `${REX_REPO:-<script-dir resolution>}`; floor_check over **full** registry.
- badge_claim_map: add invariant that online command contains `--conditions`; offline command
  names a real test file → new test `test_commands_reference_real_flags`.
- APPENDIX.md: fill disk/setup/run-time/cost; lead access with pinned tag + Zenodo; license points
  to repo LICENSE (verified in 07) or marks TODO; explicit credential-free-stops-at-Functional note;
  paper figures shown as placeholders, never invented.
