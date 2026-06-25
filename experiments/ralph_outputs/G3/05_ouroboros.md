# G3 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — Data-integrity reviewer
**Problems found:**
1. The distilled `our_pass_at_1.json` lives in B15; if B15 is purged, G3 silently
   breaks. → FIX: `load_ours()` falls back to recomputing from A1/A2 raw JSON, so the
   script is not hard-coupled to B15. (Implemented: `_pass_at_1_from_result` fallback.)
2. We headline A1 (glm-5p2) numbers; A2 (deepseek-v4-pro) gives slightly different
   fair-band values (best_of_n 0.307 vs 0.341). Cherry-picking risk. → FIX: report
   notes A2 in the narrative; the rank conclusion (bottom band, below frontier) holds
   for BOTH (A2 best_of_n 30.7% is even lower). Documented in 06/09.
3. CIs shown only for OURS rows (SREGym paper didn't publish per-row CIs). Asymmetry
   could imply false precision. → Accept as a known limitation; noted in caveats.

## Engineer B — Statistics reviewer
**Problems found:**
1. Sorting two incomparable random variables into one ordinal list is the central
   methodological sin. → MITIGATED not solved: banner + regime column make the
   incomparability explicit; the script never asserts a "win". This is positioning, not a test.
2. No significance test BETWEEN our row and a SREGym row — and none is possible (we
   lack their per-problem outcomes). → Correctly NOT attempted; stated as a blocker in 09.
3. `_wilson_ci` only used in the raw fallback path; under the distilled path CIs come
   pre-baked. Two CI provenances. → Acceptable; both are Wilson (A1/A2 used the same
   estimator). Noted.

## Engineer C — Over/under-engineering reviewer
**Problems found:**
1. `partition_breakdown` is loaded but not rendered in the table. Under-using cited
   data. → The "novel is hardest" positioning bullet uses it (ported->new collapse
   numbers). Acceptable; full partition table would bloat the ranked view (kept in report prose).
2. `_pass_at_1_from_result` handles schema variants that may never trigger (distilled
   path almost always wins). Mild over-engineering. → Kept deliberately for robustness
   if B15 is absent; cost is ~15 lines, justified by the fallback requirement A flagged.
3. No machine-readable output (only markdown). A downstream consumer can't parse ranks. →
   Minor; the markdown table is the deliverable per the task ("ranking table script").
   Could emit JSON; left out to stay focused (noted as a nice-to-have in 09).

## Final filtered spec changes
- Keep the B15-first / raw-fallback dual loader (A1, B-no fix needed).
- Report explicitly states the conclusion is robust across A1 AND A2 (A2).
- Keep partition data in prose, not the ranked table (C1).
- Accept CI asymmetry and the no-cross-benchmark-sig-test limits as documented caveats.
