# E7 — 01 Plan

## Objective
Test whether REx-style diagnose-then-act policies transfer **beyond the SRE/D&D
domains** to other interactive game domains — specifically text-adventure /
embodied-text games (TextWorld, Jericho, ALFWorld). Deliver a **domain-agnostic
trajectory adapter** plus a **transfer-experiment plan**, with a generic adapter,
a unit test, and a synthetic fixture.

## Why these domains
SRE incident response, D&D, and text adventures are the same *abstract MDP*:
sequential, partially-observed, command/tool-driven, sparse terminal reward,
with red-herring branches. If the REx tree-search + deterministic judge stack is
truly domain-general, it should ingest a TextWorld/Jericho/ALFWorld episode and
score it with no core-code change. E7 builds the bridge that makes that testable.

## Candidate datasets (survey)
| Dataset | Type | Per-step signal | Why a good transfer target |
|---|---|---|---|
| **TextWorld** (MS) | procedurally-generated text games | `feedback`, `admissible_commands`, `score` | gold walkthroughs known; difficulty knobs; cheap to generate |
| **Jericho** | 50+ real Z-machine IF games (Zork…) | `observation`, `valid_actions`, `score`, `moves` | human-authored, long-horizon, hard distractors |
| **ALFWorld** | text-aligned embodied (ALFRED) | `obs`, `admissible_actions`, goal-condition success | tests embodied/grounded transfer, not just parser games |
| (ref) **SRE/REx** | this project | `tools_used`, `reward`, `answer` | proves schema is a superset, baseline anchor |

## Approach
1. Define ONE canonical trajectory schema whose fields line up 1:1 with what
   `rex/scoring.py` already consumes (stated cause / gold / red herrings /
   actions / solved).
2. Pluggable per-domain adapter functions (`@register("textworld")` …) that
   normalize raw episode logs into the canonical schema.
3. A `to_sre_scoring_inputs()` projection so adapted game trajectories feed the
   **existing deterministic judge unchanged**.
4. Unit test + synthetic fixtures for all 4 domains, incl. a real call into
   `rex/scoring.deterministic_judge` / `mechanism_score`.

## Files to create (all task-namespaced)
- `artifacts/trajectory_adapter.py` — schema + registry + 4 adapters.
- `artifacts/synthetic_fixtures.json` — 1 episode per domain.
- `artifacts/test_trajectory_adapter.py` — pytest (12 cases).
- `artifacts/test_run.log` — captured run.

## Dependencies / risks
- **No network / no dataset download** in this env → use *synthetic* fixtures
  shaped exactly like the real loaders emit (documented field names). Real-data
  ingestion is a documented blocker, not a fabrication.
- Must NOT edit `rex/*.py` — adapter only *reads* the judge via import.
- Risk: real loader field names drift from my assumptions → mitigated by keeping
  adapters thin + table-documenting the source field names.

## Success criteria
- Adapter normalizes all 4 domains; `pytest` green.
- An adapted **game** trajectory is scored by the **real** SRE judge without
  touching core files.
- Transfer-experiment plan documents metrics, baselines, and the blocker for the
  live run.
