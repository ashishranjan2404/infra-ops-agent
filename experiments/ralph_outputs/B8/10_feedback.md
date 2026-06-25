# 10 — Feedback for the next task

The pass@k result JSONs (`by_condition[c].overall` with `n, passes, mean_reward,
reward_std`) are the canonical, self-contained substrate for any statistics task — no need
to re-run models. Two complete files exist (A1/glm-5p2 n=126, A2/deepseek-v4-pro n=150);
match a metric to the data type (Cohen's h for the binary pass@1 proportion, Cohen's d for
continuous mean_reward — never d on a 0/1 rate). The headline that keeps re-validating:
**REx is a *large* effect on every measure and every model, even against the strongest
baseline (best_of_n: h≈+1.24, d≈+1.15), while best_of_n/retry/no-oracle are
small-to-negligible** — so the project's "+0.5 reward" style claims are only impressive for
REx once standardized. The next statistics task (CIs / Hedges' g / per-family effect sizes)
should bootstrap over the per-incident reward arrays (which exist in `rex/runs/*.json` and
the A-series files) rather than the pooled overall stats, because pooling hides
within-incident seed correlation and inflates effective n.
