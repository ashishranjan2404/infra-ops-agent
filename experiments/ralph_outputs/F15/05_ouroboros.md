# F15 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer 1 — "Build-systems pedant"
**Problems found:**
- **gzip non-determinism:** `tarfile.open(mode="w:gz")` writes an mtime into the *gzip* header,
  so two runs differ even if TarInfo mtimes are 0. The spec only fixed TarInfo, not gzip. → must
  write tar to a `BytesIO`, then gzip with `gzip.GzipFile(mtime=0)`, or compress separately.
- **`\input{sections/foo}` ext resolution:** LaTeX allows `\input{x}` meaning `x.tex`. Collector
  must try `target`, then `target.tex`. Spec said "resolve .tex ext" but didn't pin order.
- **Comment stripping:** `\input` inside a `% commented line` would be a false positive. Must strip
  `%`-comments (respecting `\%`) before regex.

## Engineer 2 — "arXiv-policy realist"
**Problems found:**
- **Abstract macro check is claimed but not enforced anywhere.** Metadata says "no LaTeX macros"
  but nothing validates it. Either validate in the test or at least lint in the packager's
  metadata-adjacent check. Decision: keep metadata hand-authored & macro-free (verified by eye +
  a grep in 07); do not over-engineer a LaTeX-macro linter — out of scope, documented.
- **License ambiguity:** "CC BY 4.0 vs arXiv non-exclusive" — picking CC BY commits the authors.
  Should default to the arXiv **non-exclusive license to distribute** (safest, reversible) and
  flag CC BY as an opt-in decision, not bake it in.
- **Endorsement:** first-time arXiv submitters to cs.* need endorsement. Checklist omitted it in 01.
  Add it.

## Engineer 3 — "skeptical reviewer of the deliverable itself"
**Problems found:**
- **The headline blocker (empty sections) makes the tarball misleading.** If the script happily
  writes a tar over empty sections, a careless human posts an empty paper. Mitigation already in
  design (advisory exit 1 + READINESS block) — but the MANIFEST must put the verdict at the TOP,
  not the bottom, so it's seen.
- **Idempotency vs `dist/` reuse:** re-running appends nothing but overwrites; fine. But if `out`
  dir doesn't exist the script must `mkdir -p`. Spec implied but didn't state.
- **Author block is a placeholder.** We don't have real author identities. Honest move: metadata
  ships `authors: [{name: "TBD — fill before posting", ...}]` and the checklist's de-anonymization
  step owns it. Do NOT invent author names.

## Final filtered spec deltas (applied to implementation)
1. Deterministic gzip via `gzip.GzipFile(mtime=0)` over an in-memory tar (Eng1).
2. Input resolution order: exact path → `+.tex` (Eng1).
3. Strip `%`-comments before scanning for `\input/\include/\bibliography` (Eng1).
4. MANIFEST puts `READINESS:` verdict at the **top** (Eng3).
5. `out` dir auto-created (Eng3).
6. License default = arXiv non-exclusive; CC BY flagged as opt-in in metadata `notes` (Eng2).
7. Add **endorsement** check to checklist (Eng2).
8. Authors = explicit `TBD — fill before posting`; never fabricated (Eng3).
9. No automatic LaTeX-macro linter; abstract macro-freeness verified by grep in 07 (Eng2, scoped out).
