# B13 — 03 Improved Plan

## What changed after the grill

1. **Reframed the headline (SMR/AAAI/RLE).** The deliverable is the IAA *protocol +
   machinery + primed worksheet*, not a human IAA number. Machine-vs-machine is a smoke
   test, never presented as a validity result.

2. **Two-part machine baseline (AAAI accepted).** Instead of only the tautological
   kappa(judge,judge)=1.0, also compute kappa between `deterministic_judge` and a
   *different* deterministic grader (`mechanism_score >= 0.5`). This exercises the metric
   on real labels and yields a non-trivial number (it came out 0.917).

3. **Blinding protocol (AAAI accepted).** Document that the worksheet shipped to humans
   must hide the `machine_label` column. The generator keeps the column (for adjudication)
   but the protocol spec mandates a blinded copy. Gold root stays visible because these
   are SYNTHETIC scenarios where the gold IS ground truth (PSRE/SMR resolution).

4. **`provenance` column added (RLE/DOL).** Each worksheet row tags whether its
   stated_cause came from gold / red-herring / generic, so per-family judge-error
   breakdown is a one-line groupby once human labels exist.

5. **>=2-rater + missing-data support kept (RLE).** `krippendorff_alpha` tolerates None
   and any rater count; `fleiss_kappa` and `mean_pairwise_cohen` cover fixed panels. So
   human-vs-human and human-vs-machine compute with no code change later.

## Critiques accepted
- AAAI: machine kappa=1.0 is vacuous on its own -> added second-grader baseline + framing.
- AAAI/SMR: blinding -> documented blinded-copy protocol.
- RLE: bias matters, not just kappa -> `provenance`/`scenario` columns enable it.
- DOL: zero deps, CSV, no core edits -> honored.

## Critiques rejected (with reason)
- AAAI "human-vs-human is mandatory before shipping": REJECTED for THIS task. We have no
  annotators/budget this week; gating the deliverable on labels we can't get means
  shipping nothing. Instead the protocol REQUIRES h-vs-h and the machinery computes it the
  moment labels arrive. Blocker documented honestly (RLE's position).
- SMR "hide gold from labelers": REJECTED for synthetic scenarios — labelers can't
  re-derive truth for incidents they didn't investigate; gold is the designed ground
  truth. Only `machine_label` is blinded (PSRE's resolution).

## Final shape (unchanged files list, refined semantics)
- `iaa.py` (lib), `build_worksheet.py` (generator + baseline), `test_iaa.py` (tests),
  generated `relabel_worksheet.csv` (+ blinded-copy instructions in spec) and
  `machine_baseline.json`.
