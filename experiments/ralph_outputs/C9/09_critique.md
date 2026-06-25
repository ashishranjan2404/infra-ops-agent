# C9 — 09 Critique (honest)

## What a reviewer attacks first
1. **The synthesized harness produced nothing.** With `deepseek-v4-pro` as the mutation
   operator, all 6 Thompson nodes (both the full-42 and small-10 searches) stayed pinned at
   the seed score and `best_rules` came back **empty**. So the "synthesized" row is identical
   to the empty seed — there is **no positive AutoHarness generalization result in this run**.
   Cause is almost certainly that deepseek didn't emit a JSON rule-list that survived
   `validate_ruleset`/`_extract_json_list`, or didn't beat the seed under the 2×-weighted FA
   reward within 6 nodes. The canonical haiku operator (per the core docstring) does produce
   rules; we couldn't use it because **Anthropic credits are exhausted** (verified 400). This
   is the single biggest weakness: the headline is solid but the *synthesis* half is a blocked
   negative.
2. **Headline reframing could be seen as dodging the hard part.** The task says "report
   `is_safe` accuracy full vs small." `is_safe` is the hand-written baseline, so the headline
   is LLM-independent and easy to ship — a skeptic could say we leaned on the easy metric. Defense:
   it is literally what the task asked, and it is the most reliable, reproducible number here.
3. **Single split seed.** The full-42 70/30 split uses one seed. Held-out accuracy (0.944)
   could shift with a different draw. Multi-seed / k-fold would tighten it; deferred under the
   15-min cap. The headline whole-set accuracy is split-invariant, so this only touches the
   secondary train/held-out table.
4. **Interesting real finding (not a weakness):** hand-written `is_safe` is actually *more*
   accurate on the full 42 (0.933) than on the small 10-incident split (0.871). The small
   split is hazard-dense (it was curated around the spanning forbidden-category hazard), so it
   stresses the harness harder; the broader 42-set includes many incidents where the harness
   cleanly allows correct fixes, lifting accuracy. The constant though is the **37 false-allows
   across 580** (6.4%) — the catastrophic class the PSRE persona flagged — concentrated where
   the harness lacks a spec signal. That FA tail is the real story for an SRE audience.

## What's missing / would do next
- Re-run synthesis with the canonical haiku operator once credits return, to get a real
  full-42 synthesized-vs-handwritten comparison.
- Multi-seed full split + per-hazard false-allow breakdown on the 42-set to localize the 37 FAs.
- A guard that logs the raw LLM proposal when `validate_ruleset` rejects it, to confirm whether
  deepseek's failure was formatting vs. reward.

## Bottom line
Deliverable met for the task's literal ask (is_safe full vs small, run over all 42, no core
edits, within cap). The synthesized-harness extension is an honest **blocked negative**: real
run, no usable rules, root cause (credits) documented.
