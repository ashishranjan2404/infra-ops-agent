# 10 — Feedback for the next task

This repo carries two distinct result narratives — the optimistic frontier sweep in
`ARCHITECTURE.md` (REx lifts every model to a 0.86 ceiling) and the deflating, honest read in
`docs/headline_insights.md` (the lift is largely oracle-feedback leakage; the real
contributions are the verifiable env + searched verifier). Any presentation/marketing task
(poster, slides, abstract, demo script) MUST surface both at equal weight or it reads as
cherry-picking to a reviewer — treat `headline_insights.md` as the integrity ground truth and
`ARCHITECTURE.md` as the demo framing. Practical wins: writing a tiny stdlib validator
(HTMLParser tag-stack + a `[src:]` path-existence check) catches both malformed output and
phantom citations in one pass and makes step 07 a real test rather than a vibe; remember to
handle HTML void elements or it false-positives. Self-contained HTML (inlined CSS, system
fonts) keeps deliverables offline-openable but forces a trade-off against embedding the real
`docs/*.png` charts — next time consider base64-inlining the figures. Numbers were taken from
summary docs, not re-run (frontier needs `HUD_API_KEY` + live gateway); fine for a poster but a
data-claim task should re-execute or at least diff the docs against `rex/runs/*.json`.
