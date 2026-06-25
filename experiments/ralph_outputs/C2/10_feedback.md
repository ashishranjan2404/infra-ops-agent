# C2 — Feedback for the next task

Reuse-don't-reimplement paid off: importing `rex.harness_synth`'s machinery and only
overriding the split + model gave an apples-to-apples comparison in ~40 lines with zero
core edits. Two operational gotchas to carry forward: (1) Anthropic is 400ing (out of
credits) AND the obvious gateway fallback `deepseek-v4-pro` returns EMPTY completions for
JSON-emitting prompts (it's a reasoning model that puts everything in hidden reasoning) —
so does `gemini-3.1-pro`; the reliable gateway operators for structured-output tasks here
are `gpt-5.5` (best) and `grok-4.3`. Always smoke-test the operator returns parseable
output before trusting a "synthesis found nothing" result — a flat/degenerate score is
often a dead operator, not a real negative. (2) When you train any learned-harness on a
family subset, the headline result is *hazard coverage* (which features get supervision),
not raw rule JSON or rule count — frame comparisons that way and call out the model
confound explicitly. Finally, watch the complexity penalty: λ=0.003 was too small to stop
an over-general 0-condition `scale_deployment` blanket rule from winning on train, which
then false-blocks correct fixes on held-out.
