# C6 — 08 Verification

## Success criteria (from 01) — met?
1. **2+ proposers run synthesis end-to-end (or documented unreachable).** ✅ 3 ran
   (gpt-5.5, deepseek-v4-pro, minimax-m3); the intended haiku proposer documented
   unreachable (Anthropic credits). All real, from actual gateway/Fireworks calls.
2. **Real comparison of synthesized rule-sets + TRAIN/HELDOUT metrics.** ✅ `comparison.json`
   + 3 `synth_*.json` with rules, node trajectories, confusion matrices, held-out FA/FB
   tuples. Comparison table in 06/07.
3. **Zero edits to shared core files; driver runnable/reproducible.** ✅ Only the
   module-global `MODEL` is overridden in-process and restored in `finally` (T2). No
   `rex/*.py`, `sim/*.py`, `agent/*.py` modified.

## Are the outputs real (not placeholder)?
Yes. Each proposer produced a *different* rule-set with a *different* failure mode that
is internally consistent with the model's behavior:
- deepseek → empty rule-set (node_scores all 0.4638 = seed) → it literally never
  emitted a valid improving rule. Held-out FA=13 is the empty-harness signature.
- gpt-5.5 → added a conditionless tool-ban rule → 10 held-out false-BLOCKS.
- minimax-m3 → 3 clean general rules → 0 false-blocks, 0.897 held-out accuracy.
These are not interchangeable placeholder numbers; they trace to the actual rules.

## Primary DV per the grill: held-out (false_allow, false_block)
| proposer | ho_FA | ho_FB | reading |
|---|---|---|---|
| minimax-m3 | 4 | 0 | best synthesized harness; near baseline |
| gpt-5.5 | 4 | 10 | over-blocks correct fixes |
| deepseek-v4-pro | 13 | 0 | no harness at all (empty) |
| hand-written | 2 | 0 | reference; unbeaten |

## In-scope vs out-of-scope held-out false-allows (per Ouroboros B)
The module scopes the generalization claim to the spanning hazard
`treats_forbidden_category` (present in BOTH splits). Reading minimax-m3's 4 held-out
FAs by hazard tuple:
- `clear_cache`/`restart_pod` on cpu_saturation_leaf → `trap_action` (out-of-scope:
  trap actions aren't a feature the interpreter sees).
- `drain_node`/`cordon_node` on singleton_node_notready → `last_ready_node`
  (single-incident hazard, train-only per module docs → out-of-scope).
So minimax-m3 has **0 in-scope (forbidden-category) held-out false-allows** — it fully
generalized the spanning hazard. deepseek, by contrast, false-allows MANY
forbidden-category actions on held-out (its empty set blocks nothing) — an in-scope
generalization failure.

## Verdict
The question "does the proposer matter?" is answered **affirmatively and with margin**:
the same search yields anything from a near-baseline harness (minimax-m3) to NO harness
(deepseek-v4-pro) to an over-blocking harness (gpt-5.5). The proposer is the dominant
factor in synthesized harness quality at this budget.
