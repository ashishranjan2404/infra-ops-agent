# 10 — Feedback for the next task

Grounding the Related Work in the *actual repo source* (not just the outline) was the
highest-leverage move: `rex/harness_synth.py`, `rex/tree.py`, and `rex/scoring.py`
contain the exact mechanisms (rules-as-data + held-out accuracy; Beta-posterior
Thompson tree; deterministic keyword judge with `JUDGE_MODE`) that make each citation's
positioning *true* rather than hand-wavy — so any doc/writing task should read the code
that backs the claim before writing the claim. The one irreducible weakness of an
offline writing task is citation accuracy (real author/venue/DOI), which no validator
can confirm without web access; a future task should pair this section with a real
`references.bib` and a fetch-and-verify pass for the recent works (CWM, SREGym,
FIREBALL), and resolve the exact REx/AutoHarness provenance so those names stop reading
as potential phantom cites. The 19-token coverage validator is a cheap, reusable
anti-omission guard worth keeping for any future paper-section task.
