# J9 — Feedback for the next task

Coordination/human-access tasks have a hard ceiling for an autonomous worker: you can build a
flawless, machine-validated protocol but you cannot manufacture the human signal it needs, so
be ruthless about separating "deliverable shipped" from "outcome achieved" and say plainly in
09 that the literal goal ("get feedback") was not met even when status=completed. The highest-
leverage move was tying every survey/interview item to a small set of *falsifiable* thesis
claims with pre-registered accept/reject criteria, then writing a stdlib validator that fails
if any item is orphaned or unrecordable — that validator caught two real bugs (un-recordable
free-text follow-ups) that a human reviewer would likely have missed, which is exactly the kind
of cheap, verifiable check worth front-loading. For future human-in-the-loop tasks: design the
instrument elicit-then-reveal to avoid leading the witness, weight live-walkthrough evidence
above rated-prose, pre-register the *process* not brittle percentage thresholds, and always
provide a clearly-labelled lower-validity proxy fallback (e.g. public post-mortems for
cascade/trap realism) while naming exactly which claims the proxy CANNOT test.
