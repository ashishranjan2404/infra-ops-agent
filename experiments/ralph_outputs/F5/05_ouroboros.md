# F5 — Ouroboros: self-critique of the spec as 3 different engineers

## Engineer A — "the pedant" (formatting / counting rigor)
**Problems found:**
- A1. The word-count `sed` recipe in 04_spec is fragile: `grep -v '^#'` would also drop a
  line that legitimately starts with `#` inside prose, and the abstract is a single
  paragraph so there are no such lines — but the recipe also relies on the `---` rule
  existing *before* the count line. If the Provenance section also uses `---`, the range
  `/^# Abstract/,/^---/p` stops at the FIRST `---`, which is correct, but I must ensure
  there is exactly ONE `---` between body and the word-count line and the Provenance
  section uses `##` headings, not another `---` immediately. → **Fix:** use exactly one
  top-level `---` as the body terminator; Provenance separated by `##` only.
- A2. "Body ≥ 180" (T3) is arbitrary. Justify or drop. → **Keep but soften:** it's a
  guard against an empty/stub abstract, not a hard requirement; treat T3 as advisory.

## Engineer B — "the skeptic" (claim support / honesty)
**Problems found:**
- B1. The spec says cite "~0.90 vs ~0.95." But `headline_insights.md` §2 says "0.90
  accuracy vs 0.95 hand-written." Those ARE the doc's numbers — fine — but the spec must
  forbid me from silently importing the outline's *different* 89.7/94.9. → **Fix:** spec
  already forbids 2-dp; reaffirm I use the insight-doc pair (0.90/0.95) verbatim, framed
  as "approaching hand-written," and I will write them as ~0.9 / ~0.95 to avoid implying
  3-sig-fig precision on n=3.
- B2. The "stripped → ≈ zero-shot" claim cites `ablation.json`. I should confirm the
  ablation actually contains a no-oracle / REx-no-oracle arm with numbers near 0.25, not
  just zero_shot. The insight doc asserts it (0.25 ≈ 0.24); the JSON has the per-incident
  arms. → **Action:** in 07, grep the ablation JSON for the arm keys to confirm before
  asserting. If the no-oracle arm isn't present in the JSON, downgrade the claim to cite
  only `headline_insights.md` §3 (still a real artifact).
- B3. The benchmark is "42 incidents" in the outline, but `ablation.json` only enumerates
  5 incidents and `harness_synth.json` 10. The 42-incident benchmark is a build target
  (`build_incidents.py`), not necessarily fully materialized in these JSONs. → **Fix:**
  the abstract may cite the benchmark design (42, 12/20/10 split) since the outline §4
  describes it, but I must not imply all 42 were *run* in the results I cite. Phrase as
  "we build a 42-incident benchmark," results cited separately on the measured subset.

## Engineer C — "the editor" (over/under-engineering, readability)
**Problems found:**
- C1. The Provenance table is great for audit but risks making the deliverable look like
  a spec, not an abstract. → **Fix:** keep Provenance as a clearly-separated appendix
  under the word-count line; the abstract paragraph stands alone and reads as an abstract.
- C2. Risk of a run-on single paragraph that's technically ≤250 but unreadable. AAAI
  reviewers skim. → **Fix:** allow 4–6 sentences with strong topic transitions; prioritize
  the hook sentence and the honest-limitation sentence as standalone, punchy lines.
- C3. Over-engineering risk: T3/T5/T6 regex tests are nice but the real deliverable is one
  paragraph. Don't let test theater eat the writing. → **Resolution:** run the tests, but
  they're a checklist, not a CI gate; the human-judged quality of the paragraph dominates.

## Final filtered spec (deltas applied)
- Use insight-doc numbers verbatim, written approximately (~0.9 / ~0.95) — no 2-dp.
- Before asserting the oracle-leakage equality, **verify the ablation arm keys** (B2); if
  absent, cite `headline_insights.md` §3 alone.
- Benchmark cited as a **build/design** (42; 12/20/10), not as "all 42 evaluated."
- Exactly one top-level `---` terminating the body; Provenance under `##` headings.
- Abstract = 4–6 readable sentences, hook + honest-limit sentences kept punchy.
- Tests T1–T7 run as a checklist in 07; T3 advisory; word gate T2 is the hard one.
