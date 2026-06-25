# 10 — Feedback for the next task

The biggest leverage was that real artifacts already exist: `opensre-traj/out/hud_trajectories.jsonl`
holds 197 recorded agent runs with `answer`, `reward`, `subscores`, ground-truth category, and
source provenance — enough to build a real, blinded, *stratified* rating set without any live
cluster. When a task's deliverable depends on humans/clusters/GPUs you don't have, the winning
move is to make everything *around* the blocker real and validated (a stdlib-only scoring script
with a synthetic self-test + example-CSV path proves the pipeline end-to-end), then document the
blocker honestly rather than fabricating results. Two concrete lessons for similar studies:
(1) stratify the sample for *variance* or your inter-annotator-agreement metric collapses, and
(2) hide ground truth from raters until after submission or you leak the answer into correctness
scores — both are easy to get wrong and were caught only in the self-critique pass. Keep
deliverables stdlib-only when feasible; it makes them runnable anywhere and trivially testable.
