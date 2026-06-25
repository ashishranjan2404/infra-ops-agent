# 03 — Improved plan (post-grill)

## What changed vs 01
1. **Solvability is operational, not statistical.** Flag defined strictly as
   "no tested condition passes a single sample (best pass@1 == 0)". Docstrings and the
   markdown header avoid any claim of in-principle impossibility. Each cell carries `n`
   and `passes` so the reader can judge confidence. *(accepted: AAAI, SMR)*
2. **Dual output kept and made first-class.** Machine JSON has full per-condition
   pass@1/pass@k/mean for every (model, incident); Markdown leads with the short
   unsolvable list + a by-family rollup table. *(accepted: PSRE, RLE)*
3. **Per-condition columns retained** so "learnable-but-hard" (zero_shot fails, rex
   solves) and per-condition regressions remain visible — not collapsed into the flag.
   *(accepted: RLE, DevOps)*
4. **Explicit `--inputs` paths**, single reproducible command, no directory globbing.
   *(accepted: DevOps)*
5. **One row per (model, incident); never pool reps across models.** *(accepted: AAAI)*

## Critiques rejected (and why)
- *"Drop the unsolvable flag entirely because n=3 is too small" (AAAI R1).* Rejected:
  the task explicitly asks to *flag unsolvable incidents*. We address the concern by
  re-scoping the flag to an operational triage definition and disclosing n, rather than
  deleting the deliverable. AAAI conceded this in R2.
- *"Auto-glob all JSONs in the tree" (implied convenience).* Rejected per DevOps:
  explicit inputs only, for CI reproducibility and to avoid ingesting unrelated schemas.

## Added robustness
- Schema validation on ingest; gracefully skip (with stderr note) any file missing
  `by_condition` / `incidents_by_family`.
- Add a `partially` tier (0 < best pass@1 < 1) so the binary solvable/unsolvable split
  doesn't hide "solved sometimes, never reliably" incidents.
