# 08 — Verification against success criteria

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| 12 real, blinded, stratified diagnoses, parseable | ✅ | `diagnoses_to_rate.json`, 12 items from real `hud_trajectories.jsonl`; T3 parse/align PASS |
| Rubric has concrete anchors for every Likert point | ✅ | `rubric.md` — 1–5 behavioral anchors per dimension + binary trust item |
| Protocol covers recruitment, consent, blinding, pilot, pre-registered analysis | ✅ | `protocol.md` §3–§7 |
| Scoring script runs green on synthetic AND example CSVs | ✅ | T1 + T2 PASS; emits Krippendorff alpha + validity correlations |
| Blocker documented honestly; no fabricated human ratings | ✅ | 07/09; output `_mode` distinguishes synthetic vs real; no human CSVs claimed |

## Are outputs real (not placeholder)?
- **Diagnoses**: real — pulled verbatim from recorded agent runs (`answer` field), with real
  incident names, source companies (Slack, GitHub, Cloudflare, etc.), difficulty, and tool use.
- **Auto-rewards in the key**: real — the deterministic judge's recorded `reward`/`subscores`.
- **Rubric/protocol**: real, executable documents (not stubs).
- **Scoring script**: real, runs, tested on 6 cases; computes genuine Krippendorff alpha
  (verified degenerate=1.0) and Spearman/Pearson.
- **Example rater CSVs**: **synthetic and explicitly labeled** (`ratings_example/`, `_mode`
  provenance). They demonstrate the pipeline; they are *not* presented as human data.

## Coverage of the task ask
- "5 SREs evaluate diagnoses" → protocol specifies N=5 within-subjects crossed design.
- "protocol" → `protocol.md`. "rubric (Likert on correctness/usefulness/safety)" → `rubric.md`.
- "sample of diagnoses to rate (from real scenarios if reachable)" → reachable; 12 real ones.
- "analysis plan (IAA)" → pre-registered Krippendorff alpha + companions, in protocol + script.
- "study packet + scoring script" → delivered and validated.
- "human recruitment is the documented blocker" → documented in 03/07/09, protocol §3.

## Verdict
All success criteria met. Deliverable is a complete, validated study packet; the only thing
missing is recruited humans, which is the pre-identified, documented blocker.
