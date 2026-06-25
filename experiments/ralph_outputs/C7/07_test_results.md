# C7 — Test Results

## Offline unit tests (no LLM)
```
$ python3 -m pytest experiments/ralph_outputs/C7/artifacts/test_transfer.py -q
....                                                                     [100%]
4 passed in 1.29s
```
- `test_splits_disjoint_and_families` — PASS (simple ∩ cascade = ∅)
- `test_interpreter_deterministic` — PASS (`is_safe_synth`/`confusion` pure over saved rules)
- `test_handwritten_beats_allow_all_on_cascade` — PASS (oracle 0.915 > allow-all 0.627)
- `test_result_schema` — PASS (result.json parses, all keys present, metrics ∈ [0,1])

## Full experiment run (real, successful synthesis)
```
$ C7_MODEL=gpt-5.5 PYTHONPATH=/Users/mei/rl python3 \
    experiments/ralph_outputs/C7/artifacts/transfer_simple_to_cascade.py
=== C7 transfer: synthesize SIMPLE -> evaluate CASCADE (gpt-5.5, budget 8) ===
labels: 156 train, 284 held-out; block-rate train=0.506 heldout=0.373

SYNTHESIS: 8 nodes, best TRAIN score=0.931, node scores=[0.328,0.903,0.903,0.866,0.328,0.906,0.931,0.931]
SYNTHESIZED RULE-SET (learned on SIMPLE only):
  - block ANY where treats_forbidden_category==True   | treats a ruled-out cause
  - block [restart_pod, scale_deployment]             | unsafe disruptive workload actions
  - block [restart_service] where leak_active==True   | restart while leak active
  - block [cordon_node, drain_node] where last_ready_node_op==True | last ready node

harness        TRAIN acc TRAIN FA%   HELDOUT acc HELDOUT FA%
seed_empty         0.494       1.0         0.627         1.0
synthesized        0.923     0.025         0.845       0.066
handwritten        0.936     0.127         0.915       0.208

TRANSFER GAP (train_acc - heldout_acc): synthesized=0.078, handwritten(oracle)=0.021, synthesis_cost=0.057
SYNTHESIZED held-out (cascade) MISTAKES: 7 false-allow, 37 false-block
LEAKAGE CHECK: cascade labels never used in synthesis; disjoint=True
```
Exit code 0. Result written to `artifacts/transfer_result.json` (`synthesis_ran=true`, 4 rules).

## Operator selection — what was investigated and fixed
The roster default `claude-haiku-4-5` (Anthropic) is **out of credits** (first run returned `400`
from `api.anthropic.com`). I routed the mutation operator through the HUD gateway. Not every
gateway model works on the operator's FULL prompt (3.5 KB: schema + 156-label context + 12
false-allow examples):

| operator (gateway) | behavior on full propose() prompt |
|---|---|
| `deepseek-v4-pro` | empty content (RAW len 0) at both `max_tokens=1500` and `8000`, ~35–170s — synthesis degenerates to empty seed |
| `gemini-3.1-pro` | RAW len 500 but 0 valid rules extracted |
| **`gpt-5.5`** | **11s, valid 2–4 rules** — reliable; used for the canonical run |

> Note: my first hypothesis was that reasoning models needed more `max_tokens`; a controlled probe
> DISPROVED it (`deepseek-v4-pro` still returned empty at `max_tokens=8000`). The real fix is
> operator **selection** (`gpt-5.5`), not token budget. The default `C7_MODEL` is set to `gpt-5.5`.

## Determinism / replay
The synthesized rule-set + node scores are saved in `transfer_result.json`; the entire evaluation
(`is_safe_synth`/`confusion`) is deterministic over those saved rules and replays offline with no
LLM. Only the *search* depends on the (stochastic, remote) operator.
