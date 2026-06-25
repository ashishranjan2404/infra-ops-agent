# D2 — 07 Test Results

Env: `.venv-hud` (Python 3.12, hud 0.6.6), `HUD_API_KEY` present (len 42), live gateway.
All commands run from `experiments/ralph_outputs/D2/artifacts/`.

| # | Test | Result |
|---|------|--------|
| T1 | `python3 -m py_compile train_rft_qwen14b.py` | **PASS** exit=0 |
| T2 | `--help` (argparse, no network) | **PASS** usage printed |
| T3 | `yaml.safe_load(config)` | **PASS** `available=False requested=Qwen/Qwen3-14B substitute=Qwen/Qwen3.6-27B` |
| T4 | `--preflight` (default base Qwen3.6-27B) | **PASS** exit=**0**; lists bases; "14B present: False"; "Qwen3.6-27B present: True" |
| T5 | `--preflight --base Qwen/Qwen3-14B` | **PASS** exit=**2**; "Qwen/Qwen3-14B present: False" + BLOCKER printed |
| T6 | `--base Qwen/Qwen3-14B` (no --model) | **PASS** exit=**2**; ERROR: --model required |
| T6b | `--base Qwen/Qwen3-14B --model dummy` (no smoke) | **PASS** exit=**2**; preflight-guard aborts before any paid call |

## Live preflight output (T4, gateway-backed, real)
```
=== Trainable Qwen bases on the HUD Tinker gateway ===
  - opensre-qwen3-30b
  - opensre-qwen3-8b-1e439a
  - Qwen/Qwen3-235B-A22B-Instruct-2507
  - Qwen/Qwen3-30B-A3B
  - Qwen/Qwen3-8B
  - Qwen/Qwen3.5-397B-A17B:peft:262144
  - Qwen/Qwen3.5-397B-A17B
  - Qwen/Qwen3.5-4B
  - Qwen/Qwen3.6-27B
  - Qwen/Qwen3.6-35B-A3B
Qwen-14B (dense) present & trainable: False
BLOCKER: no Qwen-14B on this backend. Use the documented substitute (default --base Qwen/Qwen3.6-27B).
Requested base 'Qwen/Qwen3.6-27B' present & trainable: True
```

## What was NOT run (and why — no fabrication)
- **No fork, no smoke, no 30-step run.** Two reasons, both real:
  1. **Blocker:** the requested Qwen-14B does not exist on the Tinker gateway (T5 proves it).
  2. **Compute cap:** a real fork + GRPO step on the 27B substitute is paid Tinker
     forward/backward, hours for 30 steps — outside the ~15-min worker cap.
- Therefore `artifacts/runs/` is empty and `result.json` reports zero training metrics.
  The reproducible evidence delivered is the live preflight (T4) proving the substitute base
  IS trainable, so the launcher is ready to run the moment compute/approval is granted.

## Fixes applied during testing
- Initial concern: CLI table wraps at terminal width and breaks row parsing → fixed by
  forcing `COLUMNS=400` in `_cli_models_raw()` (verified: all 10 Qwen rows parse cleanly).
