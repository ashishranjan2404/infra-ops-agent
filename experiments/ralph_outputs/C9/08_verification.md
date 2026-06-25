# C9 — 08 Verification

## Success criteria vs outcome
| Criterion | Status | Evidence |
|---|---|---|
| Run harness over the **full 42 incidents** (not just 10) | MET | 42 incidents, 580 labeled examples, 253 should-block (results_full42.json) |
| Train/test split on the full set | MET | 70/30 incident split: 29 train / 13 held-out (400 / 180 examples) |
| Report `is_safe` accuracy on **full set vs small split** | MET | small-10 = **0.871** (FA 16, FB 2); full-42 = **0.933** (FA 37, FB 2) |
| Ground in `rex/harness_synth.py` | MET | runner imports core machinery; no reimplementation |
| Do NOT edit shared core files | MET | only new files under `experiments/ralph_outputs/C9/`; `git status` confirms no core diff is mine |
| Compute cap ~15 min | MET | full run 342.1s (~5.7 min) |

## Outputs are real, not placeholder
- `results_full42.json` holds concrete confusion numbers per harness per split, produced by
  the unmodified core `confusion`/`confusion_pred` over deterministically generated labels.
- The headline `is_safe` numbers are reproducible bit-for-bit via `--no-llm` (T3), proving
  they are LLM-independent and not fabricated.
- The synthesized-harness result is a genuine (negative) run: the gateway operator returned
  no improving rule-set, recorded as `best_rules=[]`, not papered over.

## Honest caveats (carried into 09)
- The "synthesized" rows used `deepseek-v4-pro` (Anthropic credits exhausted), not the
  canonical haiku operator, and it produced no usable rules — so the synthesized harness here
  is effectively the empty seed and is NOT a positive generalization result. The HEADLINE
  (hand-written `is_safe` full vs small), which the task literally asks for, is fully met.
