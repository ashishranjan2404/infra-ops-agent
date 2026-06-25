# C7 — Implementation

## What I built (real artifacts)
1. **`artifacts/transfer_simple_to_cascade.py`** — standalone cross-type transfer harness.
   - Imports `scenarios_by_family` (`rex.harness`), the synthesis machinery
     (`labeled_examples`, `confusion`, `confusion_pred`, `handwritten_pred`, `propose_ruleset`,
     `train_score`, `hazard_coverage`) from `rex.harness_synth`, and `thompson_search`
     (`rex.tree`). **Edits no shared file.**
   - Splits are computed from family labels, not hardcoded: `TRAIN = simple` (12 incidents),
     `HELDOUT = cascade` (20 incidents). Asserts disjointness (leakage guard).
   - Synthesizes the safety rule-set with `thompson_search` over **TRAIN(simple) labels only**
     (budget 8, seed 0). Cascade labels never enter `propose`/`evaluate`.
   - Scores three harnesses (`seed_empty`, `synthesized`, `handwritten` oracle) on both families;
     records the full confusion matrix, false-allow count/rate, per-family block rate, the
     transfer gap, and the synthesized rule-set + node scores.
   - Writes `artifacts/transfer_result.json`.
2. **`artifacts/test_transfer.py`** — 4 offline tests (no LLM): splits disjoint, interpreter
   determinism, hand-written oracle beats allow-all on cascade, and result-schema validity.

## Key implementation decision — model routing (documented, no core edit)
`rex/harness_synth.py:MODEL` is `claude-haiku-4-5` (Anthropic provider). The Anthropic key in
this environment is **out of credits** — the first `propose_ruleset` call returned
`400 Client Error` from `https://api.anthropic.com/v1/messages` (confirmed). Per the project's
standing note ("Anthropic out of credits → use gateway/deepseek"), the mutation operator is
routed through the **HUD inference gateway** by setting `rex.harness_synth.MODEL` at runtime from
my script (`hs.MODEL = MODEL`) — a module-level monkeypatch in MY script only; `rex/harness_synth.py`
on disk is unchanged. Overridable via `C7_MODEL=<roster-name>`.

I tested three gateway operators on the FULL `propose()` prompt: `deepseek-v4-pro` and
`gemini-3.1-pro` returned empty/invalid content (synthesis degenerates to the empty seed), while
**`gpt-5.5` reliably emits valid rules in ~11s**. (A controlled probe disproved an early
"raise max_tokens" hypothesis — deepseek still returned empty at `max_tokens=8000`; the fix is
operator *selection*, not token budget.) The default `C7_MODEL` is therefore `gpt-5.5`.

This substitution affects only the *operator that proposes rule edits*; the reward, the trusted
interpreter (`is_safe_synth`), and the scoring are unchanged and provider-independent. The
synthesized rule-set is saved so the entire evaluation replays deterministically offline.

## How to run
```bash
set -a; source ~/.zshrc; set +a
PYTHONPATH=/Users/mei/rl python3 experiments/ralph_outputs/C7/artifacts/transfer_simple_to_cascade.py
# (operator defaults to gpt-5.5; override with C7_MODEL=<roster-name>)
python3 -m pytest experiments/ralph_outputs/C7/artifacts/test_transfer.py -q
```
(The script needs `PYTHONPATH=/Users/mei/rl`; pytest picks up the repo rootdir automatically.)
