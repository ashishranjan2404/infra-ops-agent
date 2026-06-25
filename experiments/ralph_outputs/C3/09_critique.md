# C3 — 09 Critique (honest)

## What a reviewer will attack

1. **The rule language is tiny, so "generalization" is one boolean.** The synthesized
   rule that actually transfers is `treats_forbidden_category==True` — a single feature
   the hand-written `is_safe` already uses. A skeptic calls this "transfer of one bit,"
   not learned generalization. **My defense:** the contribution is *autonomy* (synthesis
   rediscovered the minimal sufficient rule from novel labels alone, with no incident
   ids, and matched the human on held-out), not rule richness. But the criticism is
   partly fair and I do not oversell: see the structural ceiling below.

2. **Structural ceiling caps held-out accuracy.** `trap_action` (the dominant blockable
   hazard, present in all 15 incidents) is a per-scenario spec list with no general
   feature; `leak_restart` needs `leak_active` AND a restart tool. Neither is fully
   expressible/learnable as a *general* rule, so held-out accuracy *cannot* reach 100%
   regardless of search quality. The 94.1% is "as good as the language allows," and I
   say so rather than implying near-perfection. Many of the `trap_action` blocks the
   synth gets right are caught only because they *also* trip `treats_forbidden_category`.

3. **The second synthesized rule is an over-generalization bug.** `block scale_deployment
   (no conditions)` blocks ALL scaling, producing 2 held-out false-blocks
   (azure/firefox cert incidents where scaling was neutral). The LLM operator added an
   unconditioned tool rule that the complexity penalty (λ=0.003) was too weak to kill
   because it didn't *hurt* the weighted TRAIN reward enough. This is a real flaw in the
   learned harness — a human wouldn't write it.

4. **2 held-out false-allows are unsafe misses.** On `media_oom_leak`, the synth lets
   `restart_pod`/`restart_service` through while the leak is active — exactly the
   "textbook fix that's actually dangerous" case. Because no `media_oom_leak`-style leak
   was in TRAIN, the operator never learned the `leak_active ⇒ block restart` pattern.
   In an SRE setting a false-allow is the worst error class; I rank this above the
   false-blocks in severity.

5. **Single model, single seed family.** I ran `gpt-5.5` (forced by Anthropic credit
   exhaustion) at budget 8, twice. Stable, but I did not sweep models or budgets, so I
   can't claim the *operator* generalizes — only that *this* run's synthesized rules do.

## What's missing / would strengthen it
- A budget/model sweep to separate "search found the boundary" from "lucky operator."
- A second novel split (rotate which 5 are held out) to show the result isn't split-specific.
- Extending the feature set so `leak_restart`/`trap_action` are *expressible* — but that
  edits shared core, which the brief forbids; documented as future work.

## Net honest verdict
A **positive but bounded** result: autonomous synthesis on certified-novel incidents
transfers the expressible safety boundary to held-out novel incidents at human-
competitive accuracy, with two named, real failure modes (one over-block bug, two unsafe
leak false-allows) that the rule language cannot currently fix. Not a clean win; an
honest, scoped one.
