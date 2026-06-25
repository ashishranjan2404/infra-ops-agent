# F10 — 10 Feedback for the next task

Coordination/sign-off tasks have no agent-executable "outcome" — the correct move is to
build a real, machine-checkable *instrument* (here: a sign-off sheet + validator +
request message) and document the human blocker honestly rather than fake an approval.
Ground everything verbatim in the named source (CLAIMS_EVIDENCE.md): copy numbers and
caveats, never invent. Put the caveat physically next to the number so over-claiming is
visible at sign-off. Surface negative/blocked results as first-class sign-off rows, not
footnotes. A status-report validator (PENDING is normal; only malformed errors) beats a
hard CI gate when most cells legitimately start unfilled. Watch for evidence that isn't
in the repo (C2's unpushed GRPO branch) — flag it as a hard blocker with a named owner,
because no sign-off is meaningful without its evidence present.
