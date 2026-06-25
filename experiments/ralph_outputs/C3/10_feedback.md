# C3 — 10 Feedback for the next task

The cleanest way to get a *defensible* generalization number was to build on A8's
certified-novel manifest rather than re-deriving novelty — reuse upstream provenance and
assert membership at runtime so the claim can't silently rot. The biggest reality check:
the synthesized-rule **language is the real ceiling**, not the search — most blockable
hazards here (`trap_action`, `leak_restart`) aren't expressible over the 6 known
features, so held-out accuracy is structurally capped and any number near-but-not-100%
should be explained, never spun. Two operational gotchas to carry forward: (1) the
default Anthropic operator (`claude-haiku-4-5`) is out of credits → use the HUD gateway
`gpt-5.5` (deepseek returned empty), and pin the model in the result JSON; (2) when a
runner needs a different model than a shared module's hardcoded `MODEL`, rebind the
module global *in-process* around the call instead of editing the core file — keeps the
parallel-safety contract. Next task should consider a *split-rotation* (rotate which
novel incidents are held out) and a budget sweep to distinguish "search found the
boundary" from "lucky single run."
