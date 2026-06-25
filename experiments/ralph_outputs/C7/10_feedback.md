# C7 — Feedback for the next task

The AutoHarness synthesis machinery (`rex/harness_synth.py`) is cleanly reusable for new
train/held-out splits by importing its functions and overriding only TRAIN/HELDOUT — no core edit
needed; `scenarios_by_family()` gives ready-made simple/cascade/novel splits. Two concrete gotchas
that will bite the next worker: (1) **Anthropic is out of credits** here, so the roster-default
`claude-haiku-4-5` operator returns `400`; route the LLM through the HUD gateway by monkeypatching
the module-level `MODEL`. (2) **Not all gateway models emit content on long prompts** — on the
full `propose()` prompt, `deepseek-v4-pro` and `gemini-3.1-pro` returned empty/invalid output
(silently degenerating synthesis to the empty seed), while `gpt-5.5` worked reliably (~11s/call);
always sanity-check that the operator returns a valid rule on the REAL prompt before trusting a
"synthesis found nothing" result. Substantively, cross-type transfer (simple→cascade) is real but
bounded: the general `treats_forbidden_category → block` rule transfers (gap ~0.08), but
target-specific `trap_action` hazards are not expressible in the shared feature set and remain
false-allows for any feature-only harness — that ceiling is the most interesting thing to report,
so always dump per-hazard held-out mistakes, not just aggregate accuracy.
