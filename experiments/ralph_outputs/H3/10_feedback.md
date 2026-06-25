# 10 — Feedback for the next task

Ground every artifact in the repo's real entrypoints before writing a line:
reading `rex/eval_pass_at_k.py` (its CLI args and its import list) is what made
the Dockerfile's COPY set and the entrypoint's `eval` subcommand correct rather
than guessed — and it surfaced that the live path needs `HUD_API_KEY` while a
deterministic offline subset (scenario loading + pass@k math) needs no network,
which became the default no-key smoke. Check `git status` for *deletions*
(root `__init__.py` was gone) so you don't bake a missing file into a COPY.
When the obvious validator is unavailable (no Docker daemon here), substitute
honest proxies — run the entrypoint/smoke natively + hadolint-style structural
assertions — and state the un-run step as an explicit blocker instead of
faking a build log. Finally, verify third-party signatures against source
(`wilson_ci` takes a proportion, not a count) rather than assuming.
