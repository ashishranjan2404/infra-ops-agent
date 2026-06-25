# B14 — Cost-Efficiency Table (pass@1 per dollar)

Metric: **pass@1 / (estimated USD per incident)** — higher = more pass@1 bought per dollar.

Cost basis: **ESTIMATED** (tokens are not logged in the result JSONs). Output-token utilization assumed at 60% of the 1400-token `max_tokens` budget. Claude prices are real; gateway/Fireworks slugs use documented assumptions (see `price_assumed`).

| model | condition | pass@1 | calls/job | $/incident | $/100 inc | cost x vs zero_shot | pass@1 per $ | price assumed |
|---|---|---|---|---|---|---|---|---|
| glm-5p2 | zero_shot | 0.2302 | 1 | $0.002568 | $0.2568 | 1.0 | 89.64 | True |
| glm-5p2 | best_of_n | 0.3413 | 4 | $0.010272 | $1.0272 | 4.0 | 33.23 | True |
| glm-5p2 | retry_realistic | 0.3492 | 2.3 | $0.005906 | $0.5906 | 2.3 | 59.12 | True |
| glm-5p2 | rex | 0.8968 | 4 | $0.010272 | $1.0272 | 4.0 | 87.31 | True |
| glm-5p2 | rex_no_oracle | 0.3333 | 4 | $0.010272 | $1.0272 | 4.0 | 32.45 | True |
| deepseek-v4-pro | zero_shot | 0.2400 | 1 | $0.002976 | $0.2976 | 1.0 | 80.65 | True |
| deepseek-v4-pro | best_of_n | 0.3067 | 4 | $0.011904 | $1.1904 | 4.0 | 25.76 | True |
| deepseek-v4-pro | retry_realistic | 0.3133 | 2.3 | $0.006845 | $0.6845 | 2.3 | 45.77 | True |
| deepseek-v4-pro | rex | 0.8933 | 4 | $0.011904 | $1.1904 | 4.0 | 75.04 | True |
| deepseek-v4-pro | rex_no_oracle | 0.2867 | 4 | $0.011904 | $1.1904 | 4.0 | 24.08 | True |

## Most cost-efficient operating point per model

| model | best condition (by pass@1 per $) | pass@1 | pass@1 per $ |
|---|---|---|---|
| glm-5p2 | zero_shot | 0.2302 | 89.64 |
| deepseek-v4-pro | zero_shot | 0.2400 | 80.65 |
