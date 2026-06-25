# G5 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the validator is theater" critic
**Problem found:** A structural validator that only checks "every cell has a `[Sn]` tag" can pass
on a matrix full of *wrong* claims with *real-but-irrelevant* citations. It verifies form, not
truth. **Fix accepted:** keep the validator (it catches the real failure mode of orphan/missing
tags during editing) but DOWNGRADE its claim in `08_verification.md` — it proves *citation
hygiene*, not factual accuracy. Add C5 (a vendor cell must be flagged `vendor-stated`) so the
validator at least enforces the honesty discipline, not just presence.

**Problem found:** `parse_matrix` will silently miscount if the markdown table has a stray `|` in
a cell. **Fix accepted:** split on `|`, strip, and assert column count == 6 (lead empty + 5)
per row; fail loudly with the offending line.

## Engineer B — "you're comparing categories you defined to win" critic
**Problem found:** The five dimensions are suspiciously aligned to our strengths (trap safety,
training method). A hostile reader sees a rigged scorecard. **Fix accepted:** two of five
dimensions (Open benchmark — tie with SREGym; Deployment posture — we *lose* to both vendors) are
explicitly ones where we are NOT first. The prose for those cells states we lose/tie. A matrix
where we lose 1.5 of 5 is credible; one where we sweep is not. Documented in the weaknesses
section.

**Problem found:** "Komodor 95% accuracy" and "Cisco 40% ticket reduction" are being cited — if
we repeat vendor numbers in our cells without flagging, we launder marketing into the matrix.
**Fix accepted:** every such number lives in the *Komodor/Datadog* column, tagged with a source
whose `verification` is `vendor-stated`, and the prose says "vendor-reported, no public
methodology." Never restated as established fact.

## Engineer C — "staleness and scope" critic
**Problem found:** Vendor capabilities are dated (Komodor self-healing GA 2025-11; Bits "deeper
reasoning" 2026-03). A matrix without dates rots in weeks. **Fix accepted:** every competitor
source carries `as_of`, and the document header states the snapshot date (2026-06).

**Problem found:** SREGym diagnosis numbers (38.9–72.6%) are from the paper's agent/model sweep,
NOT a head-to-head with us — we never ran our harness on SREGym. Implying comparability is
dishonest. **Fix accepted:** the evaluation-rigor prose explicitly says "these numbers are not
head-to-head; we have not run our policies on SREGym, nor SREGym agents on our cascades." It is a
posture comparison, not a benchmark result.

**Problem found (under-engineering):** No machine-readable output — a reviewer can't diff claims.
**Fix accepted:** `sources.json` is the machine-readable backing; that's sufficient for a
positioning doc (a full claims-graph would be over-engineering for a 5×4 table).

## Final filtered spec (deltas applied)
- Validator scope honestly downgraded to "citation hygiene + vendor-flag discipline" (Eng A).
- C5 vendor-flag check added (Eng A/B).
- Two dimensions where we tie/lose are kept and stated plainly (Eng B).
- Vendor numbers quarantined to vendor columns + `vendor-stated` tag + prose caveat (Eng B).
- `as_of` on every competitor source; header snapshot date (Eng C).
- Explicit "not head-to-head" disclaimer on the eval row (Eng C).
