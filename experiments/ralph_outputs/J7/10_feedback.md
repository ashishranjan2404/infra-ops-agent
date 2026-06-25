# J7 — 10 Feedback for the next task

Check the blocker FIRST, cheaply and read-only, before building anything: one
`gcloud projects list` revealed the temp hackathon GCP account was deleted, which
instantly reframed the task from "run the live bench" to "build the runnable offline
projection + document the blocker precisely." When a task says "run the agent against X,"
find the exact seam where a decision is currently hardcoded (here: `stages/06`'s
`eval "$(cat $FIX_FILE)"` applying the registry `fix`) and insert the agent there as a
policy with a deterministic reward you already have (the gold `fix`) — that converts a
fuzzy "run it" into a scored eval with no grading model. Always provide a `--dry-run` that
exercises the pure, no-network code path (`build_request`) so the harness is provable with
zero API/cloud cost, and a live path that's still side-effect-free (record the chosen
command, never execute it). Two gotchas worth remembering: macOS has no `timeout` (use
`--request-timeout`/per-tool flags), and the Anthropic key is out of credits while a
Fireworks model (minimax-m3) works — but minimax is a base-completion endpoint that
ignores the chat `system` prompt, so for live agent runs prefer a chat model on the
gateway path. Finally, name action-selection accuracy distinctly from the live recovery
reward so you never over-claim what an offline run measured.
