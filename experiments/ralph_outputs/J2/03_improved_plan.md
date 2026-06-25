# 03 — Improved Plan

## What changed from 01 (driven by the grill)
1. **Guarantee made structural, not flag-based (REV).** The module imports neither
   `sim.engine.apply_action` nor `subprocess`, and contains no `/ctl/fault|heal` POST.
   `test_runner_has_no_execution_imports` greps the source to enforce this. The guarantee
   is now "execution code does not exist in this module," not "a flag skips it."
2. **Observation is read-only by construction (PSRE).** `PrometheusSource` issues only a
   `GET /metrics`; it never touches `GET /` (which in this mesh would drive load and bump
   counters). Documented in the source.
3. **Diagnosis is logged (SMR).** `ShadowReport.stated_root_cause` + `observation.cascade_victims`
   + per-app `error_rate` are persisted so shadow-mode accuracy can be scored offline later
   against the known fault.
4. **Proposer injected (RLE/DOL).** `run_shadow(..., propose_fn)` takes any
   `propose_fn(Observation)->plan`. Live-LLM path is the optional `adapt_rex_propose`
   wrapper; tests + offline runs use a stub. No live key needed to prove safety.
5. **Recorded-real fixture (PSRE/DOL).** `fixture_metrics.txt` uses exact Prometheus text
   exposition matching `mreal/server.py`'s `_metrics()` output (same metric names/labels),
   for a payments-faulted cascade.

## Critiques accepted
- Structural guarantee (REV) — accepted; it's the core of the deliverable.
- Read-only observation (PSRE) — accepted; `/metrics` only.
- Injectable proposer (RLE) — accepted; enables CI proof.
- Log diagnosis (SMR) — accepted; cheap and raises the artifact's value.

## Critiques rejected (and why)
- **Plugin registry for sources (implied richer abstraction):** rejected — two dataclass
  sources is enough for the slice; a registry is over-engineering (DOL agreed).
- **"Diagnosis is the point, guarantee secondary" (SMR's strong form):** rejected for
  *priority*. The task's named deliverable is the safety guarantee; diagnosis is logged
  but the guarantee gates acceptance. (We kept diagnosis logging — just not as the headline.)

## Net result
Same three artifacts as 01, but the guarantee is enforced by tests that inspect the
source for forbidden execution paths, and the proposer is decoupled so the whole thing
runs and is provable with no cluster and no LLM key.
