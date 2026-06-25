# A9 — 08 Verification

## Against the success criteria (from 01/03)

| Criterion | Status | Evidence |
|---|---|---|
| Every incident has a row (no silent drops) | MET | 51 CSV rows == 51 YAMLs; T3 cross-check clean |
| Real incidents: cited MTTR or explicit unknown+reason | MET | 18 sourced w/ citation+confidence; 12 `unknown` each with a notes reason |
| No invented MTTR | MET | Unknown/conflated/future-dated/security-disclosure cases all left null |
| CSV->JSON build passes schema/range/invariant validator | MET | T1 VALIDATION OK; T2 shows it fails loudly on bad input |
| Correlation stub runs on repo assets, drops unknowns transparently | MET | T4: paired=18, 33 drops printed with reasons |
| No shared-core edits | MET | Only files under A9/artifacts/ created |

## Are the outputs real (not placeholder)?
- The CSV labels are **real, individually sourced facts**: e.g. Cloudflare WAF 2019
  global kill switch at 14:09 UTC after 13:42 onset = 27 min; Monzo 13:10-14:49 BST =
  99 min; AWS S3 2017 ~4h17m; Roblox 73h. Each row names the org + report.
- The scripts **execute and produce real output** (validator summary, JSON sidecar,
  correlation numbers), not stubs that print TODO.
- The one explicitly *placeholder* element is the **default difficulty proxy** in the
  correlation script — and it is labelled as such in code and in 09; the real signal
  is plugged via `--scores`. This is by design, not a hidden gap.

## Honesty checks
- Coverage is reported (60% of real incidents have known MTTR), not hidden.
- Confidence tiers (high/medium/low) distinguish documented exact windows from
  approximate/staged recoveries.
- Suspected date/signature conflations (AWS Kinesis 2024 vs 2020; GitHub 2016 DNS;
  future-dated LaunchDarkly 2025) are flagged as unknown with the reasoning, not
  force-fit to a famous number.
