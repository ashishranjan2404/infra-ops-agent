# C6 — 10 Feedback for the next task

The single most useful move was probing model reachability FIRST: the memory note was
right — Anthropic is out of credits, so any task whose default path runs `claude-*`
(here `MODEL = "claude-haiku-4-5"`) will 400 unless you reroute to the HUD gateway
(gpt-5.5, deepseek, gemini, grok) or Fireworks (glm-5p2, minimax-m3). Build the probe
into step 1 of every LLM-touching task. Second, the cleanest way to ablate a single
LLM hook without editing shared core files is to import the module and override its
module-level global in a task-namespaced driver with a `finally`-restore — surgical,
reproducible, parallel-safe. Third, watch the compute budget shape: reasoning proposers
on the gateway cost ~100–240s per 8-node search while Fireworks minimax was ~5s, so put
the slow models last and write each result to its own file immediately so a cap-timeout
never loses completed rows. Finally, when reporting synthesis quality, lead with
held-out false-allow AND false-block COUNTS (not accuracy) and read them back to the
actual synthesized rules — that's what exposed gpt-5.5's over-blocking and deepseek's
empty harness, which a single accuracy number would have hidden.
