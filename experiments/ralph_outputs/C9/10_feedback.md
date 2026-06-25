# C9 — 10 Feedback for the next task

Decouple the deterministic part of any harness/eval from the LLM part up front: the
hand-written `is_safe` evaluation over all 42 incidents needed zero API calls and gave the
headline in ~5s, so it should never be blocked by credit/gateway issues — gate only the
*synthesis* on the LLM and always ship the deterministic number. Anthropic credits on this
machine are exhausted (HTTP 400 "credit balance too low"); the HUD gateway (`deepseek-v4-pro`,
`gpt-5.5`) is the working fallback for `agent.llm.call`, but note that swapping the mutation
operator can silently yield an empty rule-set — if a search collapses to the seed score across
all nodes, log the raw LLM proposal before `validate_ruleset` to tell a formatting failure from
a genuine no-improvement. Also confirm the *real* incident universe programmatically
(`len(rex.harness._SCENARIOS)`) rather than trusting a directory file count — the YAML dir has
~51 files but the harness only knows 42. Background long LLM runs and write planning/critique
files while they execute to stay inside the compute cap.
