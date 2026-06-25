# B4 — Improved Plan (post-grill)

## What changed vs 01_plan.md

### Accepted critiques
- **(RLE) Read pre-computed `by_family`, don't re-estimate.** The stratifier now pulls the
  `pass@1/2/5`, CI, mean_reward, reward_std straight from each result JSON's
  `by_condition[c].by_family[type]` block — guaranteeing the B4 tables are byte-identical to
  A1/A2's published numbers. No second pass@k implementation.
- **(REV) Primary-type ordering rule, stated explicitly.** A single 3-way label requires a
  priority because novel∩cascade is non-empty (e.g. facebook_bgp_backbone). Rule:
  `novel > cascade > simple`. An incident is **novel** if A8 marks it held-out OR its
  `meta.source` is a dated real-world outage; else **cascade** if `assertions.cascades==true`
  and >1 SLO node; else **simple**.
- **(SMR/REV) Coverage honesty.** Classify all 51 YAMLs. The stratifier lists
  classified-but-unevaluated incidents per type so dropping the 19 unrun incidents is explicit.
- **(REV CIs / SMR spread) Every table cell carries Wilson CI and reward_std.**
- **(DOL) Exclude `.partial`** from headline tables; report it separately as provisional.
- **(SMR/REV) Mismatch report**: cross-check our type labels against each result's
  `incidents_by_family`; emit disagreements rather than trusting one side.

### Rejected critiques (and why)
- **(SMR R1) "Add a recomputed-from-raw pass@k for robustness."** Rejected — RLE is right that
  recomputing invites drift from A1. The canonical numbers already exist in the result JSON;
  recomputation adds risk, not signal. (SMR conceded this in R2.)
- **(REV) "Add a between-type significance contrast / hypothesis test."** Deferred, not in scope:
  B4 asks for *3 tables*, not an inferential comparison. We report CIs so a reader can eyeball
  overlap; a formal contrast is a separate analysis task. Documented as a limitation in 09.

## Final classification ordering (authoritative)
```
for each generated/*.yaml:
  if id in A8.heldout AND family known -> use registry/A8 family   (32 labelled)
  elif filename has '-leaf-'   -> simple
  elif filename has '-cascade-'-> cascade
  elif meta.source is dated real outage (company + year) -> novel
  elif assertions.cascades and len(slo nodes) > 1 -> cascade
  else -> simple
attach A7 difficulty_bucket if id matches (enrichment only)
```

## Deliverables (unchanged location: B4/artifacts/)
classify_incidents.py, incident_types.{csv,json},
stratify_pass_at_k.py, stratified_{simple,cascade,novel}.md, stratified_pass_at_k.json,
classification_mismatch report embedded in stratified_pass_at_k.json.
