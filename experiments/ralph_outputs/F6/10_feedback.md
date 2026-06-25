# F6 — 10 Feedback for the next task

A "formatting" task is really a content-fidelity task: the deliverable is only as good as the
numbers and claims it encodes, so ground everything in vetted repo sources
(`docs/headline_insights.md`, `ARCHITECTURE.md`) and cite the exact run file for every figure —
don't invent F1–F5 artifacts that don't exist on disk. When the obvious validation path
(here, `pdflatex`) is missing, write a *real* validator and prove it discriminates with
negative smoke tests rather than asserting "it parses"; a checker that only ever passes is
worthless. For license-restricted dependencies (the AAAI style), ship a guarded stub plus a
loud non-compliance warning so the package is runnable now without ever masquerading as
submission-ready. Finally, be explicit about what was *not* verified (PDF compile, page count,
uncited body claims) — the honest blocker is part of the deliverable, and the next task should
budget for a TeX toolchain if a true compile is required.
