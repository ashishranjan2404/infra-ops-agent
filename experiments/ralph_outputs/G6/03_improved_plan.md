# G6 — 03 Improved Plan

## What changed after the grill

**Accepted critiques:**
- **(SMR, REV) Evidence framing, not behavior slander.** Re-cast the "gaps" section into three explicit buckets: *Acknowledged*, *Not disclosed* (absence of public evidence — labeled as such), and *Structural* (inherent to investigate-the-live-incident design). We will NOT claim Bits acts unsafely or trips traps — only that trap-avoidance/escalation correctness is *not publicly evaluated*.
- **(DOL, RLE) Loud concession.** Add an explicit "Where Bits clearly leads" section: GA product, 2,000+ customer environments, tens of thousands of investigations, 8+ data sources, RBAC/HIPAA, 3–4 min autonomous investigations. Our claim is narrowed to *adversarial-cascade correctness + graduation*.
- **(REV) Frozen ≠ universally better.** Reframe frozen-policy as "*reproducibly measurable*" vs online learning as "adaptive but a moving target you cannot benchmark reproducibly." No claim of superiority, only of measurability.
- **(PSRE) Center the victim-vs-cause failure mode** as the *class of incident* where our reward design is differentiated, citing `ARCHITECTURE.md`'s thesis line.

**Rejected critiques (with reason):**
- **PSRE's "headline = trap-avoidance behavior":** rejected as the *headline* because (per SMR) we have no evidence Bits acts unsafely; using it as the headline would be straw-manning. Demoted to "axis Datadog does not publicly evaluate."
- **SMR's "headline = missing F1":** rejected as the *sole* headline (per DOL/PSRE) because operators don't consume F1; correctness-on-hard-cascades is the sharper frame. F1/judge-agreement absence is kept as supporting evidence, not the thesis.

## Revised deliverable structure (artifacts/bits_ai_sre_analysis.md)
1. Summary of Datadog's claims (sourced, exact quotes).
2. Where Bits clearly leads (honest concession).
3. Gaps/limits — bucketed: Acknowledged / Not disclosed / Structural.
4. How SRE-Degrees differentiates — each point cites a real repo file.
5. Fair verdict: complementary, not strictly "better."

## Success criteria (unchanged + tightened)
- Every claim row in `claims_table.csv` has a source URL and a fair `type`.
- At least one explicit concession.
- Each differentiator cites a real file path that exists in the repo.
- `validate.py` passes.
