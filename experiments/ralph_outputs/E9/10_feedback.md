# E9 — 10 Feedback (for the next task)

When a task pits a *measurable* arm against one that needs an external dataset or a training
stack this offline frozen-LLM worker doesn't have, don't fake symmetry — build the runnable
arm fully, wire the blocked arm to score on the *identical* metric vector (so the gap is data/
compute, not design), and frame the verdict as **data-quality / seeding**, never trained
accuracy. Two reusable patterns paid off: (1) mirror an existing reward rubric as pinned local
constants with a source citation instead of importing core code — keeps the artifact offline
AND avoids touching shared files; (2) make every synthetic group carry within-group reward
spread by construction (1 positive + graded negatives incl. the scenario's real trap), since
spread is the unit of trainability and a no-spread group is dead weight. Biggest honesty trap
to flag forward: a hand-listed canonical vocabulary made `label_coverage` read 0.10 when the
data really covers 15 mechanisms — always surface the raw covered set so a naming mismatch
doesn't masquerade as a diversity deficit. Open follow-up worth a future task: quantify the
synthetic arm's *reasoning* diversity (tool-sequence entropy across positives), which is its
true weakness, and actually feed a sample of these trajectories to the frozen LLM to confirm
they read as plausible incidents.
