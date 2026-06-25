# 10 — Feedback for the next task

Two concrete, reusable learnings. (1) **Always launch long real runs with `python3 -u`**
(or `flush=True`): when stdout is redirected to a file it block-buffers, so a working
multi-minute sweep looks "hung" for 8+ minutes with an empty log — I wasted a run chasing a
phantom hang that was just buffering. (2) **Budget by measurement, not guess**: a single
REx(budget-3) episode on a reasoning gateway model is ~30–120s (cascade incidents and
gateway latency variance push the high end), so a 2-model × 2-incident × 3-seed subset is
~9 min — right at the edge of a 15-min cap. Probe one episode's wall time *before* sizing
the sweep, exclude Anthropic-direct models (HTTP 400 / out-of-credits on this machine — use
gateway: deepseek-v4-pro, gpt-5.5), and drop high-latency models (gemini) from the *timed*
run. (3) **The pass@1 lens beat mean reward exactly as hypothesized** — a model with
positive mean reward can have pass@1 = 0 (never resolves first-try); future eval tasks
should headline pass@1 + Wilson CI, keep n visible (the n<k pass@k extrapolation returns
1.0 and will mislead otherwise), and add the `rex_no_oracle`/`novel`-family conditions if
compute allows, because oracle-fed REx saturates at 1.000 and leaves no headroom to
discriminate strong policies.
