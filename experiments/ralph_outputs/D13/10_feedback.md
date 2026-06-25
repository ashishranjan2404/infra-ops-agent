# D13 — 10 Feedback for the next task

The deterministic judge in `rex/scoring.py` is a bag-of-stemmed-words overlap
classifier, so any task touching diagnosis reward should assume it is blind to
negation (stopword 'not'), commitment/hedging (naming gold + herrings together still
passes at ~93%), component-vs-mechanism binding, and non-ASCII tokenization — a clean
adversarial string hits `mechanism_score=1.0` and `judge=CORRECT`. The single most
load-bearing methodological lesson: any "reward hacking" claim collapses without a
human-oracle baseline AND fool-rate-0 guard cases proving the oracle isn't rigged to
disagree, plus an honest reachability caveat (constructing an exploit string ≠ the RL
policy discovering it; and the diagnosis term is only 30% of reward, capping a
diagnosis-only hack). For a follow-up, the highest-value real experiment is a live
ablation comparing judge reward vs. held-out human-graded diagnoses across training to
measure whether the hedge exploit actually emerges — note it needs GPU/cluster time and
possibly LLM credits (hybrid/llm judge modes), which were the blockers here. The probe
harness pattern (force `JUDGE_MODE=deterministic`, import core read-only, write a
task-namespaced `*_results.json` + pinning pytest) is reusable for any judge/robustness
audit and stays parallel-safe.
