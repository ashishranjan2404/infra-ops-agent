# D9 — 10 Feedback for the next task

Reusing a prior task's artifact (A12's `curriculum_order.json`) was the highest-
leverage move — it turned "curriculum learning" from an open-ended training job
into a tractable scheduling + comparison-infra job that fits the 15-min/no-GPU
cap. When the real deliverable (gradient training) is blocked, the winning
pattern is: build the *real* runnable inputs (schedule + GRPO config) and a
comparison harness with a **one-function seam** to the blocked component, then
run a *transparently labeled* simulation as a proxy — never smuggle simulated
numbers in as measured reward. Bake the falsifiable hypothesis into the unit
tests (curriculum AUC > random AUC) so the mechanism is asserted, not just
printed. Next tasks touching training should check for an available GPU/Tinker
backend early and, if absent, default to this "real-config + labeled-proxy +
real-eval seam" shape rather than faking curves. Also: low absolute proxy numbers
read as failure unless the difficulty-mismatch caveat is stated up front — label
optics matter.
