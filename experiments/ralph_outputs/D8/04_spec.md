# D8 — 04 Technical Spec

## A. Input schema (assumed FIREBALL record, jsonl)
Subset of fields the adapter reads (all optional unless noted):
```jsonc
{
  "combat_id": str,
  "speaker_id": str,
  "before_utterances": [str, ...] | str,   // narration before
  "commands":          [str, ...] | str,   // Avrae command(s) — LOAD-BEARING
  "after_utterances":  [str, ...] | str,   // narration after
  "before_state": [ {name, hp?, effects?, ...}, ... ] | str,   // LOAD-BEARING (one of)
  "after_state":  [ {name, hp?, effects?, ...}, ... ] | str,   // LOAD-BEARING (one of)
  "automation_results": str
}
```
A record is **usable** iff `commands` is non-empty AND at least one of
`before_state`/`after_state` is present. Otherwise it is skipped (counted).

## B. Output schema (training-format jsonl)
```jsonc
{
  "messages": [
    {"role":"system",    "content": SYSTEM_PROMPT},
    {"role":"user",      "content": "STATE_BEFORE: ...\nCONTEXT: ...\nACTION: ..."},
    {"role":"assistant", "content": "RESULT: ...\nNARRATION: ...\nSTATE_AFTER: ..."}
  ],
  "reward": float,            // data-quality weight in [0,1] (NOT a game score)
  "meta": {"source":"fireball","combat_id":..,"speaker_id":..,"state_changed":bool}
}
```
This matches the chat-`messages` shape consumed by the project's trainer.

## C. Function signatures (`fireball_adapter.py`)
```python
@dataclass
class TrainingExample:
    messages: list[dict[str,str]]
    reward: float
    meta: dict
    def to_json(self) -> dict: ...

def _fmt_state(state) -> str            # actor-list -> "Name(hp=..)[effects]; ..."
def _reward_for(rec: dict) -> float     # data-quality weight in [0,1]
def adapt_record(rec: dict) -> TrainingExample | None   # None if unusable
def adapt_stream(records: Iterable[dict]) -> Iterator[TrainingExample]
def convert_file(in_path, out_path) -> {"records_in","examples_out","skipped"}
def main(argv) -> int                   # CLI: --in --out
```

### Reward function (documented, deterministic)
```
0.4  command present
0.2  before_state present
0.2  after_state present
0.2  before_state != after_state  (observable transition — the transferable bit)
-> min(sum, 1.0), rounded to 4 dp
```

## D. Config contract (`fireball_sft.config.yaml`)
- `data.is_real_fireball: false` — a real run MUST refuse fixture data.
- `data.min_examples_for_real_run: 2000` — below this only `--smoke` allowed.
- `eval.split_by: incident_class` (cascade/multi-hop vs simple).
- `eval.metrics: [pass@1, pass@2, pass@5]`.
- `eval.baselines`: zero_shot / opensre_trained / fireball_trained.

## E. Test cases (`test_fireball_adapter.py`)
1. fixture loads -> 7 records.
2. no-command record -> skipped (None).
3. no-state record -> skipped (None).
4. non-dict / None -> skipped.
5. basic shape: roles == [system,user,assistant]; markers present; reward in [0,1].
6. state-change detected -> meta.state_changed True, reward == 1.0.
7. no-state-change (miss) -> state_changed False, reward == 0.8.
8. fireball multi-target -> all actors + effects rendered.
9. stream filters unusable -> 6 of 7.
10. convert_file roundtrip -> (7 in, 6 out, 1 skip); every line valid json.
11. malformed jsonl line -> dropped, good line kept.

## F. Blocker contract
The real corpus is absent. The adapter/config/test run end-to-end on the
synthetic fixture ONLY. No Fireball training result is produced or claimed.
