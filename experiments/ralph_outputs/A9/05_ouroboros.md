# A9 — 05 Ouroboros (self-critique as 3 different engineers)

## Round 1 — Data Engineer
**Problems found:**
- (P1) CSV is the source of truth but nothing guarantees `incident_id` matches the
  YAML's `meta.id`. A typo silently breaks the join. -> Add T3: cross-check every id
  against the YAMLs.
- (P2) Empty `mttr_minutes` is ambiguous between "unknown" and "0". -> Spec: ""
  parses to `None`/`null`; validator forbids mttr<=0. Resolved.
- (P3) No invariant linking `mttr_minutes` presence to `confidence`. A row could have
  a number but confidence=unknown. -> Added invariant: present MTTR => confidence not
  in {unknown, not_applicable}.

## Round 2 — SRE / Incident Historian
**Problems found:**
- (P4) Over-precise MTTRs imply false accuracy. Azure 2012 leap-year and Firefox
  add-on armagaddon were *staged* multi-day recoveries; a single minute figure is
  lossy. -> Keep the number but set `mttr_basis=approximate`, `confidence=medium`,
  and state the staging in notes. Honest, not fabricated.
- (P5) AWS "Kinesis 2024-07-30" likely conflates the famous 2020-11-25 us-east-1
  event. Assigning the 2020 MTTR to a 2024 label would be wrong. -> Mark unknown,
  note suspected conflation. (Under-claiming beats mis-attributing.)
- (P6) LaunchDarkly 2025-10-20 is future-dated relative to analysis date -> no
  postmortem can exist -> unknown with that reason.

## Round 3 — Research Methodologist
**Problems found:**
- (P7) The structural proxy is nearly constant (most real incidents -> 5-node
  cascade => proxy≈10), so default correlation is low-variance and not meaningful.
  Risk: a reader treats the stub's printed r as a result. -> Document loudly in code
  docstring + 09 that the default proxy is a *placeholder*; the real signal is
  external pass@k/step-count via `--scores`.
- (P8) n=11 known MTTR; Spearman on 11 points is fragile. -> 09 critique states this;
  output reports n explicitly; no p-value emitted.
- (P9) Outage-level MTTR vs per-node sim SLOs is a unit mismatch. -> notes + 09
  caveat; this is a construct-validity limit, acknowledged not hidden.

## Final filtered spec (changes folded in)
- Added id<->YAML cross-check test (T3).
- Added MTTR/confidence linkage invariant.
- `approximate` basis + medium confidence for staged multi-day recoveries.
- Future-dated / conflated incidents -> unknown with explicit reason.
- Code + critique flag the structural proxy as a placeholder and refuse a p-value.
All other spec elements survive unchanged.
