# 05 — Ouroboros (self-critique, 3 engineers)

## Engineer A — correctness / data integrity
**Problem found:** `_records_from_yaml` reads only `trap_actions[0]`. If a scenario
declares multiple traps with different tools, the secondary traps are silently
dropped → undercounts. **Also:** G4 path likewise stores one trap per record.
**Resolution:** Acceptable for v1 — every scenario in the corpus declares exactly
one trap tool (verified: 51 files, 51 single-tool traps). Documented as a known
limitation, not a silent bug. If multi-trap scenarios appear, extend to iterate all
`trap_actions`.

## Engineer B — taxonomy soundness / over-engineering
**Problem found:** Mapping four failover tools (`failover`, `promote_replica`,
`switch_to_standby`, `drain_node`) that don't exist anywhere in the repo is
speculative — it could mislead a reader into thinking these are real tools.
**Resolution:** Keep them (completeness so future scenarios classify without code
edits) BUT the doc explicitly states failover-trap has **0 instances** and the tools
are "mapped for completeness." No misleading claim of coverage. Accepted with the
honesty caveat rather than removed.

## Engineer C — honesty / reporting
**Problem found:** A naive report would say "taxonomy of 4 categories, all
populated" — false. It must surface (a) 94% scale-trap skew, (b) zero failover
coverage, (c) flat penalty means no per-category reward signal. **Without these the
deliverable is a vanity artifact.**
**Resolution:** Accepted fully. `build()` emits `dominant_category`, `skew_fraction`,
and `empty_categories`; the runner prints `EMPTY (no coverage): ...`; the doc has a
dedicated "Honest assessment" section leading with the failover gap and the
degenerate-reward implication.

## Final filtered spec delta
- Document single-trap-per-scenario limitation (A).
- Keep failover tool map but label it 0-coverage / completeness-only (B).
- Make skew + empty categories + flat-penalty caveat first-class outputs (C).
