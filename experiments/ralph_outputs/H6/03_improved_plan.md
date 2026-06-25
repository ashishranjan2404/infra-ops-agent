# H6 — 03 Improved Plan

## What changed after the grill

**Accepted:**
- **Explicit scope = acceptance-only.** H6 validates load + schema + engine-acceptance, NOT
  fix-efficacy. Docs and code comments name A16 as the semantic (`fix_resolves`) layer so a green
  H6 is never misread as "the fix works." (SMR, AAAI, RLE)
- **Exercise the action space as a crash check.** Each `canonical_fix` step is pushed through
  `apply_action` in stage `apply_fix`; framed as "runs without raising", not "resolves". (RLE)
- **Three distinct exit codes**, with **no-match → exit 2** (silent-success trap closed). (DOL, PSRE)
- **One-command CI ergonomics**: `ci_check.sh` wrapper, `--json` artifact, stdlib + pyyaml only,
  no env vars / venv required. (DOL)
- **Per-stage failure categorization** (`load | schema | instantiate | apply_fix | settle`) so a
  red build points at the exact broken stage. (PSRE)
- **`validate()` raising is itself a schema failure**, not an uncaught crash. (robustness)

**Rejected (with reason):**
- *Fold the fix-resolves semantic check into H6* (SMR's R1 ask): rejected. It couples build health
  to research-in-progress (reward tuning) and duplicates A16. H6 stays the load-bearing wall;
  A16 stays the semantic paint. PSRE's separation argument won.
- *Validate live-cloud (chaos) fields against a real cluster*: out of scope for a CI unit gate and
  would need GKE/LKE; H6 is the offline Tier-A acceptance gate only.

## Final design (unchanged core, sharpened contract)
Staged per-scenario pipeline over the dual-glob corpus
(`scenarios/cidg/*.yaml` + `scenarios/cidg/generated/*.yaml`), reusing `sim/spec.py` and
`sim/engine.py` verbatim (read-only). Structured JSON report + human stdout + CI exit code.
Self-tests assert every exit code and every early failure stage using committed negative fixtures.
