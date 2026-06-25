# G6 — 07 Test Results

## T1–T3, enum, dangling-ref, required-files — `validate.py`

```
$ cd experiments/ralph_outputs/G6/artifacts && python3 validate.py
VALIDATE PASS  (6 sources, 18 claims, types=['acknowledged_limit', 'capability', 'not_disclosed', 'quant', 'structural'])
EXIT=0
```
PASS — all 18 claims resolve to a source, all 5 required types present, all 6 differentiator
repo files exist.

## JSON parse
```
$ python3 -c "import json; json.load(open('sources.json')); print('sources.json OK')"
sources.json OK
```
PASS.

## T4 (soft) — every source cited inline in the analysis
```
S1 cited  S2 cited  S3 cited  S4 cited  S5 cited  S6 cited
```
Initially S4 (press release) was in the table but not in prose; **fix applied** — added an
inline `[S4]` citation. Now all 6 cited.

## T5 — differentiator file paths exist (from repo root)
```
OK rex/scoring.py   OK rex/escalate.py   OK rex/loop.py
OK sim/engine.py    OK ARCHITECTURE.md   OK agent/llm.py
```
PASS. (A first run from the `artifacts/` cwd reported MISSING — that was a relative-path
artifact of the persisted shell cwd, not a real miss; the validator resolves REPO 4 levels up
and passed, and re-running from repo root confirmed all present.)

## Fact-check of quoted numbers against sources
- "≈2x faster, 3–4 minutes" → S3 (deeper-reasoning post). Verified.
- "up to 95%" MTTR decrease → S2. Verified.
- "90% faster" root causes → S1. Verified.
- "2,000+ customer environments, tens of thousands of investigations" → S6. Verified.
- Reward constants `0.30/0.25/0.45/0.60` → quoted verbatim from `rex/scoring.py`. Verified.

All tests pass; one fix applied (S4 inline citation).
