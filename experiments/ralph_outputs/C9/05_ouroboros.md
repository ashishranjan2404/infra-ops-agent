# C9 — 05 Ouroboros (self-critique, 3 engineers)

## Engineer A — "the split is arbitrary"
**Problem:** A single `seed=0` 70/30 split makes the full-42 numbers sensitive to which
incidents land in held-out. One unlucky split could put all `mem_leak` incidents in train and
report misleadingly clean held-out.
**Fix accepted:** The *headline* (task's actual ask) is whole-set `is_safe` accuracy, which is
split-invariant — it scores all 580 examples regardless of split, so the arbitrary-split risk
does not touch the headline. The synthesized train/held-out is explicitly labelled illustrative,
seed pinned and reported, and we note multi-seed would tighten it (deferred under the 15-min cap).

## Engineer B — "you changed the model, so 'synthesized' is not the core harness"
**Problem:** Core `harness_synth.py` uses `claude-haiku-4-5`. Swapping to `deepseek-v4-pro`
means the synthesized rule-set is not the canonical one; comparing its accuracy to the published
`harness_synth.json` would be apples-to-oranges.
**Fix accepted:** We never compare to `harness_synth.json`. The output records `synthesis.model`
and `09_critique.md` states plainly that the synthesized rows are "same objective, different
proposal operator (Anthropic credits exhausted)". The interpreter + reward are the unmodified
core functions, so the *evaluation* is faithful even if the *proposal distribution* differs.

## Engineer C — "false_allow_rate divide-by-zero / empty rule edge"
**Problem:** If a split has zero blockable examples, `false_allow_rate` divides by zero; if the
LLM returns an empty/invalid rule-set, `best=[]` and `synthesized` collapses to `seed`.
**Check:** `hs.confusion` already guards `nb` (returns 0.0 when `nb==0`) — verified in source.
`best=[]` collapsing to seed is *correct and informative*: it shows synthesis found no improving
rule, which is a real negative result we report rather than hide.
**Fix accepted:** No code change needed; documented the empty-ruleset semantics in `09`.

## Final filtered spec
No spec change. Three guards confirmed already present (FA-rate divide guard, validate_ruleset
fail-safe, gateway smoke-test → graceful no-LLM fallback). The only residual weakness — single
split seed for the synthesized half — is acknowledged, not silently dropped, and does not affect
the LLM-independent headline.
