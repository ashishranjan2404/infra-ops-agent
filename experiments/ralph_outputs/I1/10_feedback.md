# 10 — Feedback for the next task

Grounding a "conceptual" formalization in the *exact* existing symbols (`failed_checks`,
`clean_win`, `outcome`, `escalation_report`, `singleton_node_notready`) is what keeps it from
becoming hand-wavy — read those files in full first, then make every definition cite one. The
biggest leverage was turning the formalism into a small, dependency-free *executable* reference
impl + pytest: it forced the predicates to be precise, caught the subtle "perfect n=5 must NOT
graduate" point, and made the worked examples regressions rather than prose. Mirror core
semantics in a standalone artifact rather than importing core modules — that satisfies the
parallel-safety / no-core-edit rule for free and makes the artifact self-contained. Be
explicit and honest about small-n: the project's headline (0.86) is a *mean reward*, not a
graduation certificate, and saying so is more valuable than overclaiming. One watch-out for the
next worker: the repo's `git status` shows pre-existing `M`/`D` on core `rex/*.py` from the
branch baseline — don't mistake those for your own edits; verify by confirming your writes are
confined to your task dir.
