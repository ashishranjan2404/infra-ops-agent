# F7 — 10 Feedback for the next task

Grounding the rebuttal in *exact repo numbers* (the flat `0.522 → 0.491` RFT trace, the
`0.86 = (4×1.0+0.30)/5` fixed point, the reward weights, the 5×5 sweep, the 51+19 spec corpus)
is what separated a real artifact from generic AAAI boilerplate — read ARCHITECTURE.md and the
relevant source before writing, not after. The most valuable structural move was splitting
"severity" into *probability* (will a reviewer say it?) vs *depth* (is it fatal?), which the
grill surfaced through genuine REV-vs-PSRE disagreement; future doc tasks should look for an
analogous orthogonal-axis split instead of a single ranking. A lightweight stdlib validator paid
off twice: it caught a brittle label-regex *and* a body-extraction bug on first run, so even for
a prose deliverable, write a structural+substance checker and a negative control — it converts
"looks done" into "verified done." Finally, be disciplined that anticipating an attack ≠
answering it: tag every mitigation as promise vs. evidence so the artifact isn't mistaken for
proof the weaknesses are resolved.
