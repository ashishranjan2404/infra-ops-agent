# E6 — 06 Implementation

## Artifacts created (all under `experiments/ralph_outputs/E6/artifacts/`)

| file | what it is |
|---|---|
| `fireball_ablate.py` | Three pure deterministic transforms (`full`, `state_only`, `action_only`) over the FIREBALL/opensre trajectory record + a CLI. The genuinely new piece E6 owns. |
| `fixture_fireball.jsonl` | 2-record synthetic fixture in the exact schema (OOM + bad-deploy incidents). Lets tests run with no cluster/data. |
| `test_fireball_ablate.py` | 16 pytest unit tests on the transforms (purity, partition, channel-stripping, dispatch, validation). |
| `run_ablation_e6.py` | Ablation harness: reads a corpus, emits the 3 variant JSONLs, reports structural stats + the blocker. |
| `_variants/`, `ablation_report.json` | Emitted variants + report for the fixture. |
| `_variants_real/`, `ablation_report_real.json` | Emitted variants + report for the 319-record in-repo opensre corpus (proves it generalizes). |

## Design realized
- **Trajectory steps partition strictly**: assistant steps (thought+action) → `action_only`;
  tool steps (results/evidence_ref) → `state_only`. Provable: `assistant + tool == full`.
- **Remediation key-split**: `state_before/after`, `recovery_check`, `primary_metric`,
  `direction`, `resolved` → state_only; `fix_tool`, `canonical_fix`, `trust_tier` → action_only.
- **Evidence** → state_only only. **Gold action sequence** (`answer.optimal_trajectory`,
  `required_queries`) → stripped from state_only. **`answer.model_response`** (diagnosis
  label / target) → retained in all variants per ouroboros decision.
- **Purity**: every transform deep-copies; the input record is never mutated.

## Shared-core safety
No edits to `rex/*.py`, `sim/*.py`, `agent/*.py`, `experiments/*.py`, status files, or any
other task dir. The harness *reads* `opensre-traj/out/trajectories.jsonl` read-only and writes
only under E6/. No proposed core changes needed (E6 is purely additive data tooling).

## How a human runs it
```bash
cd experiments/ralph_outputs/E6/artifacts
python3 -m pytest test_fireball_ablate.py -q
python3 run_ablation_e6.py --in fixture_fireball.jsonl --outdir ./_variants --report ./ablation_report.json
# when the real FIREBALL corpus lands:
python3 run_ablation_e6.py --in <FIREBALL_corpus>.jsonl --outdir ./_variants_real
```
