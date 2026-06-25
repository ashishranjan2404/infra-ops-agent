# B6 — 10 Feedback for the next task

The highest-leverage move was reading `rex/scoring.py:_traps_in` and `failed_checks` FIRST and
discovering the judge already emits a `"trap_action"` token that `rex/loop.py` writes per
iteration — so the standalone metric could *consume the judge's own labels* rather than
re-derive them, and grounding came almost for free. Mirror-don't-import (plus an equality test
against the real predicate) satisfied both the parallel-safety rule and drift-prevention at
once; future metric tasks should default to that pattern. When no real rollout data carries the
fields you need, generate REAL episodes from the canonical YAMLs (canonical_fix vs trap_actions)
and label them with the same predicate — honest and reproducible — rather than fabricate numbers;
just disclose clearly that the *policy* is synthetic while the *labels* are real. Watch for
scenarios where the canonical fix tool equals the trap tool on the same target (here:
`incidentio-anetd-cpu`, `multi-fdexhaust-cpustarve`) — a metric can usefully surface such
design ambiguities, and the next task touching CIDG scenario design should investigate them.
The clearest unfinished thread is the attempted-vs-executed trap distinction over
`blocked_actions` — a natural B-series follow-up.
