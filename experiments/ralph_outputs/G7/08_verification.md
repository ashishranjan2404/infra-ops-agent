# G7 — 08 Verification

## Against success criteria (from 01/03)
1. **Brief covers required topics, every hard claim cited** — ✅ Company/funding, positioning, capabilities,
   architecture, ecosystem, customers/metrics, leadership, REx-relevance, not-knowable, sources. 10 sources
   [S1]–[S10]; funding/valuation dual-sourced (vendor + TechCrunch + Bloomberg).
2. **Vendor metrics tagged + customer-named** — ✅ 7 `(vendor-reported)` tags; Coinbase 72% and DoorDash 87%
   kept separate with distinct attributions; `>2x` accuracy labeled vendor-reported & unverified.
3. **Watch-list valid + ≥7 items w/ source+signal+cadence+verifiability** — ✅ 8 items, validator exit 0.
4. **Epistemics in structure** — ✅ `verifiability` field per item; concrete `not_publicly_knowable` list (8 entries).
5. **Honesty boundary present** — ✅ explicit "NOT publicly knowable" in both brief and YAML; REx-relevance
   flagged "we have NOT benchmarked against them."
6. **No shared core files edited** — ✅ all artifacts under `G7/`; nothing in `rex/`, `sim/`, `agent/`,
   `experiments/*.py`, status/dashboard touched (verified below).

## Outputs are real, not placeholder
- `validate_watchlist.py` actually executes and parses the real YAML (exit 0).
- Every claim in the brief traces to a real, dated public source fetched during research; the May-21-2026
  PR Newswire release was fetched directly for capability/date/metric extraction.

## Containment check
```
$ git status --porcelain | grep -v 'experiments/ralph_outputs/G7/' | wc -l   # expect 0 NEW changes from this task
```
(Run in step 07 context; this task created only files under G7/. Pre-existing repo working-tree
changes are unrelated to G7 and were not made by this task.)

**Verdict: meets all success criteria.** The deliverable is a real, validated, source-cited intel asset.
