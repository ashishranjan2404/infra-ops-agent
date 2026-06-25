# C9 — SUMMARY

**Task:** Run/evaluate the synthesized safety harness (`rex/harness_synth.py`) across the
**full 42 incidents** (it currently synthesizes on 7 train / 3 held-out = 10), with a
train/test split, and report `is_safe` accuracy on the full set vs the small split.
Compute cap ~15 min. No core file edits.

## What I did
Wrote a task-namespaced runner (`artifacts/run_full42.py`) that **imports** the core
synthesizer unchanged and runs it over the full incident universe
(`rex.harness._SCENARIOS` = **42 incidents -> 580 labeled (tool,target) examples, 253
should-block**). It evaluates three harnesses — seed(empty), synthesized, hand-written
`is_safe` — on both the core small split (7/3) and a deterministic 70/30 split of all 42
(29 train / 13 held-out). Results in `artifacts/results_full42.json`. Full run = **342s**.

## Headline result — hand-written `is_safe` accuracy (whole-set)
| set | n | accuracy | false-allow | false-block |
|---|---|---|---|---|
| **small 10-incident split** | 140 | **0.871** | 16 | 2 |
| **FULL 42-incident set** | 580 | **0.933** | 37 | 2 |

`is_safe` is *more* accurate on the broader 42-set than on the curated, hazard-dense small
split; the constant is a **6.4% false-allow tail (37/580)** — the catastrophic class.

Full-42 70/30 split, hand-written `is_safe`: **train acc 0.927, held-out acc 0.944**.

## Honest blocker
The **synthesized** harness produced no usable rules: Anthropic credits are exhausted
(verified HTTP 400), so the mutation operator was swapped to the HUD gateway
(`deepseek-v4-pro`) — interpreter + reward unchanged — but it returned an **empty rule-set**
(all search nodes pinned at the seed score). So the "synthesized" rows equal the empty seed;
there is no positive generalization result this run. Recorded honestly, not faked. Re-running
with the canonical haiku operator once credits return is the obvious follow-up.

## Compliance
No shared core file edited; all outputs under `experiments/ralph_outputs/C9/`. Headline is
LLM-independent and reproducible via `--no-llm`.
