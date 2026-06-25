# D7 — 05 Ouroboros (self-critique as 3 engineers in sequence)

## Engineer A — "the data-integrity engineer"
**Problems found:**
1. **`mixed` pool can accidentally include the eval incidents.** `exemplar_block_for`
   builds the `mixed` pool from `all scenarios` and only `n_exemplars` of them; it does
   NOT subtract eval names. If a sampled mixed exemplar coincides with an eval incident,
   that's leakage in the `mixed` baseline → unfair comparison.
2. **`build_split` uses one RNG instance, then `exemplar_block_for` uses `Random(7)`**
   for `mixed`. The mixed pool is therefore *not* the same incidents as cascade's
   `train_names`, so "mixed" and "cascade" don't even share the cascade exemplars. Is
   that intended? It means the contrast confounds pool-identity with pool-family.
3. **Empty-pool edge:** if `n_exemplars >= family_size`, `train_names` is truncated to
   `family_size − 1`; fine, but `n_eval_incidents` could then exceed remaining → cell
   with fewer incidents than requested, silently.

**Fixes applied:** (1) acknowledged as a real leakage gap in the `mixed` baseline —
see filtered spec; (2) documented as a known confound (pool identity vs family); (3)
acceptable — cells report their actual `n`, so shrinkage is visible, not hidden.

## Engineer B — "the statistics reviewer"
**Problems found:**
1. **Wilson CI with n≈8–12 is enormous.** Any reported H1/H2 delta will almost
   certainly have overlapping CIs. The deliverable risks looking like "no result."
2. **`reward_std` uses `pstdev` over a mix of incidents and seeds** — it conflates
   between-incident difficulty variance with within-incident sampling variance. As a
   "trainable signal" proxy it's crude.
3. **pass@1 = passes/n pools across incidents**, so 1 easy incident passing all seeds
   can dominate a 2-incident cell. Per-incident pass rates would be more honest.

**Fixes applied:** (1) framed as *direction-only, under-powered* in verification +
critique; full-budget knobs documented to tighten CIs. (2)(3) kept simple for the cap;
logged as future per-incident breakdown. The std is reported as a coarse spread flag,
not a formal trainability claim.

## Engineer C — "the integration / ops engineer"
**Problems found:**
1. **`_SCENARIOS` private import.** `make_exemplar` reaches into `rex.harness._SCENARIOS`.
   That's reading a private symbol — brittle if core renames it, and feels like the
   "don't touch core" rule's spirit. But it's read-only and there's no public accessor
   for `symptom`/`gold_root`. Acceptable with a comment; documented.
2. **No wall-clock guard inside the harness.** If the full sweep is launched it can blow
   the 15-min cap with no early exit. Mitigated by running a *reduced* config, not by
   code — a `--max-seconds` would be better.
3. **`agent.llm.call` lazy import** is good (dry-run needs no key), but a missing
   `HUD_API_KEY` only fails at first real call, deep in the loop — late failure.

**Fixes applied:** (1) kept with an explicit comment; it's the only way to get
`symptom`/`gold_root` without editing core. (2) documented as a known limitation; the
delivered runs are sized under the cap. (3) acceptable for a research harness; the
brief's env-load step covers the key.

## Final filtered spec (deltas from 04)
- **Known limitation (Eng A #1):** the `mixed` baseline does not subtract eval names
  from its pool → possible minor leakage in `mixed` only. The `cascade` and `none`
  configs are leakage-clean. Documented in 04→here and 09; does not affect the H1
  result (which uses cascade vs none, both clean). H2 uses `mixed`, so H2 is the
  weaker of the two claims — stated explicitly.
- **Statistics (Eng B):** report deltas as direction-only at default budget; CIs wide.
- **Ops (Eng C):** private `_SCENARIOS` read documented; runs sized under cap; no
  in-code time guard (future `--max-seconds`).
Everything else in 04 stands.
