# B4 — Stratified pass@k by incident type — Plan

## Objective
Split pass@k results by incident type (**simple / cascade / novel**) into **3 separate
stratified tables**. Two sub-deliverables:

1. A **classifier** that assigns every incident in `scenarios/cidg/generated/` to one of
   the 3 types, reusing the A7 difficulty sidecar and A8 novelty/family sidecar where present,
   and falling back to a deterministic rule for incidents those sidecars don't cover.
2. A **stratifier script** that reads available pass@k result JSONs (A1 full run, A2 ablation,
   any partials) and emits **3 separate per-type pass@k tables** (Markdown + JSON), one each
   for simple, cascade, novel — each with n / passes / pass@1 (+ Wilson CI) / pass@2 / pass@5 /
   mean_reward / reward_std per condition.

## Why this is non-trivial (not just re-printing A1's by_family block)
- A1/A2 results already contain a `by_family` block, but only for the **42 incidents they ran**.
  `scenarios/cidg/generated/` contains **51 YAML files**, of which only **32 are in
  `registry.json`** (the labelled set the harness loads). The remaining **19** (the `80-89`
  real-outage series + the 6 `a11-pair-*` transfer files) are **unlabelled** and need a
  deterministic classification so the corpus is fully stratified.
- The task explicitly asks to *classify incidents in `scenarios/cidg/generated/`* — i.e. cover
  the whole generated corpus, then render the 3 tables from whatever results exist.

## Approach
1. **Classify** (artifact `classify_incidents.py`): for each `*.yaml` in generated/:
   - Tier 1 (authoritative): family from `scenarios/cidg/generated/registry.json`.
   - Tier 2: A8 `heldout_split.csv` `family` column (same labels; cross-check).
   - Tier 3 (fallback for the 19 unregistered): deterministic rule —
     - filename contains `-leaf-` → **simple**; contains `-cascade-` → **cascade**
       (a11 pairs self-describe).
     - else read the YAML: `assertions.cascades == true` AND >1 SLO node → **cascade**;
       single SLO node / leaf root → **simple**; real-world `meta.source` outage with a
       famous company + `assertions.cascades` → **novel** (these are the post-2019 real
       incidents = genuinely novel substrate).
   - Attach A7 `difficulty_bucket` (easy/medium/hard) where the id matches (enrichment, not
     used for the 3-way split — difficulty is orthogonal to type).
   - Emit `incident_types.csv` + `incident_types.json` (file, id, type, source_tier, difficulty).
2. **Stratify** (artifact `stratify_pass_at_k.py`): load every result JSON under
   `experiments/results/` and `experiments/ralph_outputs/*/artifacts/*pass_at_k*.json`.
   For each model/run, pull its `by_condition[*].by_family[simple|cascade|novel]` block and
   render **3 separate Markdown tables** (one per type) across conditions + a combined JSON.
   Validate the result's `incidents_by_family` against our classifier (flag mismatches).
3. **Run** both scripts, capture real output, write 3 tables to artifacts.

## Files to create (all task-namespaced under B4/artifacts/)
- `classify_incidents.py`, `incident_types.csv`, `incident_types.json`
- `stratify_pass_at_k.py`, `stratified_simple.md`, `stratified_cascade.md`,
  `stratified_novel.md`, `stratified_pass_at_k.json`

## Files to modify
- NONE. Read-only on `rex/*`, `sim/*`, `registry.json`, A1/A2/A7/A8 artifacts.

## Dependencies
- Python 3.13 stdlib only (csv, json, glob, yaml). `pyyaml` is in requirements-rex.txt.

## Risks
- A result JSON's family classification could disagree with our classifier → mitigate by
  emitting a mismatch report rather than silently trusting either.
- Some unregistered incidents have no run results → they appear in the classification but not
  the pass@k tables (honest: "classified, not yet evaluated").

## Success criteria
- Every `*.yaml` in generated/ gets exactly one type label (51/51 covered).
- 3 separate pass@k tables produced from REAL A1/A2 result numbers, not placeholders.
- Scripts run clean; classifier counts cross-check against registry.json and A8.
