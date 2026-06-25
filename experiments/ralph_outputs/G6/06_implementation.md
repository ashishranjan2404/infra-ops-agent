# G6 — 06 Implementation

## What I built (real artifacts, all under G6/artifacts/)

1. **`sources.json`** — 6 validated sources: 5 Datadog primary (S1 launch blog, S2 build/
   engineering blog, S3 deeper-reasoning update, S4 press release, S5 product docs) + 1
   independent (S6 Help Net Security). Every URL https; ids unique.

2. **`claims_table.csv`** — 18 machine-checkable rows. Columns: `id, claim, type, source_id,
   our_position`. Types span `capability` (C1–C6,C11), `quant` (C7–C10),
   `acknowledged_limit` (C12), `not_disclosed` (C13–C15), `structural` (C16–C18). Every row
   carries a resolving `source_id` and our fair counter-position. Quant rows are pinned to the
   *specific* source post (e.g. the 3–4 min / 2x number → S3, not the launch post).

3. **`bits_ai_sre_analysis.md`** — the deliverable. Five sections: (1) sourced summary of
   Datadog's claims with exact quotes; (2) explicit concession of where Bits leads; (3)
   gaps bucketed into Acknowledged / Not-disclosed / Structural; (4) our differentiation with
   each point citing a real repo file and the exact reward constants; (5) a fair "complementary,
   not strictly better" verdict that states the no-empirical-head-to-head caveat.

4. **`validate.py`** — hard validator: parses both files, HARD-fails on any dangling
   `source_id`, enforces the `type` enum, requires ≥1 capability + ≥1 quant + ≥1 gap type, and
   asserts the 6 differentiator repo files actually exist on disk.

## Research method
WebSearch + 5 WebFetch passes over the primary + independent URLs. Every quantitative claim was
captured with its exact phrasing and attributed to the post that made it. Differentiators were
grounded by reading `ARCHITECTURE.md`, `rex/scoring.py` (reward weights verbatim),
`rex/escalate.py` / `rex/loop.py` (escalation outcome), and `rex/harness.py` (the held-out
`singleton_node_notready` no-safe-fix incident).

## Shared-core compliance
No shared core file edited. All new content is task-namespaced under
`experiments/ralph_outputs/G6/`. Repo source files were read-only references.
