# 10 — Feedback for the next task

Grounding deliverables in the actual ground-truth artifacts (here, the 51 CIDG YAMLs)
pays off twice: it makes the output trustworthy and it surfaces honest findings the
paper must own — e.g. the substrate is 40/51 synthetic, severity is a near-constant
0.7, and the real-named incidents still ship with empty `urls`. Build extraction
defensively from the start (`.get()` + per-file try/except), key rows on filename not
`id` (ids repeat across the 80/81/82-prefixed files), and emit both a human format
(markdown) and a machine format (JSON) so the artifact is both a paper exhibit and a
CI diff gate. Next task: if it touches these specs, consider proposing a `.patch` that
adds real postmortem URLs to the named incidents (cloudflare/github/slack/aws) — that's
the single highest-leverage realism fix, but it's a shared-core change so it must be
delivered as a documented patch, not an in-place edit.
