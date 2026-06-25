# B10 — 10 Feedback for the next task

The biggest leverage was grounding the metric in what the logs *actually contain* before writing any
plot code: the RFT JSONL records a continuous weighted reward, not pass@1, so the whole task hinged
on one modeling decision — derive pass@1 by thresholding, and reuse the repo's existing τ=0.8 (from
`rex/eval_pass_at_k.py` / `experiments/compute_pass_at_k.py`) rather than inventing one. Two lessons
for the next worker: (1) always check the reward *ceiling* of real logs first — here max reward
≈0.78–0.80 made the canonical 0.8 bar unachievable, turning the headline curve flat-zero, which would
have looked like a bug if I hadn't reported the range and added a labeled lower-threshold companion;
resist the urge to move the bar just to make the figure climb (that's reward-hacking your own plot).
(2) The parallel-safety rule against editing shared core files is real and limiting — the genuinely
better fix (per-incident logging in `train_rft*.py`) was off-limits, so I mirrored
`compute_pass_at_k`'s Wilson/threshold math into a self-contained artifact and documented the
proposed core change instead of making it. Keep deliverables self-contained, read shared files but
never write them, and prefer an honest null result with a working harness over a fabricated upward
curve.
