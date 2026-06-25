# A8 — 03 Improved Plan

## What changed vs 01
1. **Tiered novelty criterion** replaces single string-match (grill: RLE, SMR, PSRE).
   - Tier 1: exact id match (normalized) OR a *significant token-pair* overlap
     (>=2 shared meaningful tokens) with any training incident → contaminated.
   - Tier 2 (HARD): company/vendor identity axis. If the cidg incident names a
     company present in training (`github`, `cloudflare`, `slack`, `aws`,
     `datadog`, `circleci`, `incidentio`, `launchdarkly`, ...), the real-world
     source org is not novel → contaminated, regardless of mechanism.
   - Tier 3 (SOFT): `failure_class` reuse is recorded as `tier3_failure_class_seen`
     and only hard-enforced with `--strict-class`. (SMR/RLE compromise.)
2. **Stop-list of generic tokens** ("cache", "cert", "disk", "leak", ...) so a
   novel incident isn't excluded for sharing a generic infra word. (grill risk)
3. **Two scripts**: builder + an independent `assert_no_overlap.py` that
   re-derives the training set itself. Added a **negative control**. (DVO)
4. Manifest now records **training_stats**, **stratification by family**, and a
   **manifest_sha256** for auditability. (REV)

## Critiques accepted
- Match on semantics not ids (RLE) — accepted; the two corpora use different id
  namespaces, pure id-match would falsely declare everything novel.
- Company axis as hard novelty signal (PSRE) — accepted; public post-mortems mean
  same-org test items are effectively seen.
- Independent guard + negative control (DVO) — accepted.

## Critiques rejected (with reason)
- "Exclude every seen failure_class" (strict SMR reading) — **rejected as default**.
  The curriculum reuses ~15 classes by design; hard-excluding them holds out
  almost nothing and removes the ability to measure within-class generalization.
  Compromise: keep it as a recorded flag + `--strict-class` option.
- "N<10 is fatal" (REV) — **rejected**; 13–15 mechanism-distinct incidents incl.
  genuinely unseen real-world events is adequate for a stress eval, and we
  stratify by family so the reader can judge.

## Deliverables unchanged
Builder, guard, manifest.json, split.csv — all under A8/artifacts/.
