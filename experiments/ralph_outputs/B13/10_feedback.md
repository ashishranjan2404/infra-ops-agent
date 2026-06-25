# B13 — 10 Feedback for the next task

IAA on a deterministic judge is a trap: machine-vs-machine kappa is tautologically 1.0,
so don't sell it as a result — frame it as an idempotence sanity check and add a SECOND
independent grader to get a non-trivial number that exercises the metric on real labels
(judge vs `mechanism_score>=0.5` gave 0.917 here, a genuinely useful baseline). The real
validity result needs human labels, which is a hard external blocker; the right move is to
ship a tested, zero-dependency scoring library plus a primed, blinded worksheet built from
REAL scenarios and the REAL judge, so the human study is a drop-in when annotators exist —
and to say plainly that the headline number is blocked rather than fabricate it. Two
reusable patterns for downstream tasks: (1) `rex.harness.load_scenario` + `rex.scoring`
imports give clean read-only access to all 42 scenarios and the judge without touching
core files — ideal for parallel-safe analysis artifacts; (2) when a task's main result is
human/cluster/GPU-gated, the deliverable is a runnable apparatus + honest blocker, and that
should be designed (multi-rater + missing-data support up front) so the next worker adds
data, not code. Watch the easy-panel pitfall: synthetic gold-paraphrase rows inflate
agreement; mix in real model-trace diagnoses for the contestable cases.
