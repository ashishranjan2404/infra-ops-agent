# G1 — Improved Plan (post-grill)

## What changed vs 01_plan.md

1. **Framing (accepted, AAAI+RLE).** The adapter exposes our policy as an explicit
   **"non-interactive planner" entry**, NOT a like-for-like leaderboard claim. Every
   output carries the caveat that SREGym reference agents (Claude Code, Stratus, Codex)
   are interactive MCP tool-users while ours is a plan policy. This is a transfer/
   zero-shot result, labeled as such.

2. **Validity: real observation bundle (accepted, AAAI).** Added an
   `ObservationGatherer` interface to the adapter. Our `build_prompt` normally feeds a
   pre-baked alert snapshot; SREGym deliberately withholds that, so the adapter must
   construct the prompt from a *gathered* observation (metrics/logs/traces/kubectl)
   rather than a leaked spec. Shipped as an interface + a documented stub
   (`StubGatherer`) so the contract is testable offline.

3. **Dynamic resource binding (accepted, DOL).** The action translator is split:
   - a STATIC table mapping our tool semantics -> a kubectl/MCP command *template*;
   - a runtime `TargetResolver` (interface + stub) that resolves logical targets
     (e.g. `checkout`) to concrete `namespace/deployment` via `kubectl get` at run time.
   No static dict pretends to know per-problem resource names.

4. **Paired metrics (accepted, PSRE).** The run plan reports diagnosis%, mitigation%,
   E2E%, AND harmful-mitigation-rate AND escalation-rate together. Escalation is never
   reported alone.

5. **Out-of-action-space handling (accepted, PSRE).** Problems whose mitigation cannot
   be expressed in our 12-tool action space (TiDB/MongoDB/Kafka internals, OS/hardware
   faults) are tagged `N/A (out of action space)` — reported, never silently scored 0
   or faked.

## Critiques rejected (and why)
- **SMR's "measure escalation only on the New partition" single-axis story.** Rejected
  because (PSRE) a trivial all-escalate agent would score perfectly on "no harmful
  mitigation." We keep escalation paired with solve-rate.
- **A fully static tool->resource dict.** Rejected (DOL) — per-problem/per-app resource
  names require runtime discovery; the dict only encodes tool *semantics*.
- **AAAI's "must wrap in a multi-turn agent or it's invalid."** Partially rejected:
  we do NOT rebuild our policy as a tool-using agent (out of scope, changes the very
  thing under test). We instead satisfy AAAI's *underlying* concern (don't leak withheld
  structure) via the ObservationGatherer, and we label the entry non-interactive.

## Revised deliverable list (unchanged paths, refined contents)
- `artifacts/sregym_adapter.py` — `SREGymPlannerAdapter` with: `ObservationGatherer`
  (+`StubGatherer`), `TargetResolver` (+`StubResolver`), `build_diagnosis()`,
  `translate_action()`, `translate_plan()`, `run_problem()` (dry-run capable).
- `artifacts/action_translation.json` — static tool -> kubectl/MCP template + which
  tools are expressible vs out-of-action-space.
- `artifacts/test_sregym_adapter.py` — pytest: imports, every tool translates,
  diagnosis string built, dry-run `run_problem` returns the right contract, OOA tagging.
- `artifacts/run_plan.md` — exact cluster steps + paired-metric reporting.
- `artifacts/RUN_PLAN_blocker.md` — the documented blocker + what would unblock it.
