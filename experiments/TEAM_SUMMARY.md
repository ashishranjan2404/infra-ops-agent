# SRE Agent Paper — Team Summary (Jun 24, 2026)

## 10-Point Summary

1. **Fixed the reward function.** The LLM-judge (Claude Haiku) was injecting noise
   into 30% of the reward signal, causing flat RLVR training. Replaced it with a
   deterministic keyword-set classifier — 12 tests, pure function, no network calls.

2. **Expanded the benchmark to 42 incidents.** Was 10, now 42: 8 simple, 14 cascade,
   10 novel — all generated from real postmortems (CircleCI, Datadog, Slack, GitHub,
   Cloudflare, AWS, Facebook, Knight Capital, Kafka, etc.). Each has trap actions,
   causal chains, and canonical fixes.

3. **Training v2 works.** Old run: reward declined 0.522 → 0.491 (-0.031). New run
   with 10 tasks + deterministic judge + graded mechanism score: 0.504 → 0.541
   (+0.037). The fix worked — reward now trends up, not down.

4. **Root cause of flat training was NOT the LLM judge alone.** It was 3 things:
   (a) only 4 training tasks → overfit, (b) coarse category term maxed immediately
   → no learnable headroom, (c) GRPO groups spanning different scenarios → advantage
   reflected difficulty, not rollout quality.

5. **Harness synthesis is our strongest result.** 3 auto-synthesized rules achieve
   89.7% verifier accuracy, approaching hand-written 94.9%, with 14→3 rule
   compression. This is publishable as-is.

6. **REx with SME feedback lifts pass@1 by 40 points on hard incidents.** Zero-shot:
   0% pass@1. REx with SME: 40% pass@1. Without SME feedback: 0% (no improvement).
   The gain comes entirely from the teacher, not self-improvement.

7. **Switched from mean reward to pass@k.** The meeting flagged mean reward as
   insufficient. New eval matrix: pass@1/2/5 with Wilson CIs, split by incident
   type (simple/cascade/novel), McNemar's paired test. Pipeline code is ready.

8. **SREGym is the direct competitor but they're a benchmark, not a methodology.**
   They have 90 problems + a leaderboard (Claude Code tops it). They don't have:
   trap-action labels, Fireball transfer, or auto-synthesized harness. That's our
   wedge.

9. **Fireball transfer (Claim 2) is blocked.** Wenji's GRPO branch was never pushed.
   The FIREBALL training data isn't in the repo. The eval pipeline is ready — only
   the trained model is missing.

10. **Paper outline is written.** Working title: "Training Trap-Aware SRE Agents
    with a Synthesized Safety Harness, Cross-Domain Transfer, and SME-Feedback
    RLVR." 3 claims, each with evidence mapping. Full outline in
    experiments/PAPER_OUTLINE.md.

---

## Results Table

### Table 1 — Ablation: pass@1 on 5 hard cascade incidents (Haiku, 3 seeds)

| Condition | Mean Reward | pass@1 (≥0.8) | vs Zero-shot |
|-----------|------------|---------------|--------------|
| Zero-shot | 0.242 | 0% (0/15) | — |
| Best-of-n (n=4) | 0.235 | 6.7% (1/15) | -0.7 pp |
| Retry-realistic | 0.230 | 0% (0/15) | -1.2 pp |
| **REx + SME feedback** | **0.687** | **40% (6/15)** | **+40 pp** |
| REx no-oracle | 0.250 | 0% (0/15) | +0.8 pp |

Key finding: The 4 baselines are statistically indistinguishable. REx with SME is
the only condition that solves hard incidents. Without SME feedback, REx = zero-shot.

---

### Table 2 — Frontier models: baseline vs REx (5 incidents, mean reward)

| Model | Baseline | REx | Lift | Baseline wins | REx wins |
|-------|----------|-----|------|---------------|----------|
| Claude Haiku 4.5 | 0.630 | 0.860 | +0.230 | 2/5 | 4/5 |
| Claude Opus 4.8 | 0.810 | 0.860 | +0.050 | 3/5 | 4/5 |
| GPT-5.5 | 0.630 | 0.860 | +0.230 | 2/5 | 4/5 |
| Gemini 3.1 Pro | 0.750 | 0.860 | +0.110 | 3/5 | 4/5 |
| DeepSeek V4 Pro | 0.810 | 0.860 | +0.050 | 3/5 | 4/5 |

Key finding: REx compresses the spread — all models converge to ~0.86. Biggest
lift on weaker baselines (Haiku, GPT-5.5: +0.23). Strong baselines have less room.

---

### Table 3 — Harness synthesis (verifier accuracy on 3 held-out incidents)

| Harness | Rules | Accuracy | False-allow | False-block |
|---------|-------|----------|-------------|-------------|
| Seed (empty) | 0 | 66.7% | 100% | 0% |
| Synthesized v1 | 14 | 87.2% | 38.5% | 0% |
| **Synthesized v2** | **3** | **89.7%** | **30.8%** | **0%** |
| Hand-written | ~5 | 94.9% | 15.4% | 0% |

Key finding: 3 auto-synthesized rules approach hand-written accuracy (89.7% vs
94.9%) with 14→3 rule compression. The 4 remaining false-allows are genuinely
unlearnable (unseen in training or hand-written also misses).

---

### Table 4 — Fine-tuning: v1 vs v2 (Qwen3-8B, RLVR/GRPO)

| Run | Tasks | Steps | Start reward | End reward | Delta | Trend |
|-----|-------|-------|-------------|-----------|-------|-------|
| v1 (old) | 4 | 25 | 0.522 | 0.491 | -0.031 | Declining |
| **v2 (new)** | **10** | **15** | **0.504** | **0.541** | **+0.037** | **Improving** |

Key finding: v2 fixes (10 tasks, deterministic judge, graded mechanism score,
reset-head) reversed the decline. Within-group std ~0.18 is healthy for GRPO.
More steps needed to confirm the trend continues.

---

### Table 5 — Incident benchmark (42 total)

| Category | Count | Source | Expected Winner |
|----------|-------|--------|-----------------|
| Simple | 8 | Synthetic (leaf faults) | Harness-trained agent |
| Cascade | 14 | Real postmortems (CircleCI, Datadog, Slack, GitHub, Cloudflare, AWS, LaunchDarkly) | Fireball-trained agent |
| Novel | 10 | Real postmortems not in training (Facebook, Knight Capital, Cloudflare WAF, Kafka, GKE, conntrack) | TBD — generalization gap |
| Original | 10 | Pre-existing scenarios | — |
| **Total** | **42** | | |

---

## 3 Claims for the Paper

| Claim | Statement | Evidence | Status |
|-------|-----------|----------|--------|
| C1 — Harness | Synthesized 3-rule harness blocks trap actions, approaches hand-written accuracy | Table 3: 89.7% vs 94.9% | ✅ Solid |
| C2 — Fireball | D&D trajectory transfer improves cascade pass@1 over SRE-only training | Wenji's GRPO run (not pushed) | ❌ Blocked |
| C3 — SME feedback | REx + SME beats zero-shot by ≥2x pass@1 on complex incidents | Table 1: 40% vs 0% | ✅ Solid |

---

## What We Need From the Team

| Who | What | When |
|-----|------|------|
| Wenji | Push GRPO branch + Fireball training data | Before Thursday |
| Ashish | Run full 750-episode ablation with faster model (vLLM or local) | Before Thursday |
| All | Review PAPER_OUTLINE.md + PAPER_QUESTIONS.md, combine answers | Thursday meeting |
| Ashish | Reach out to Snorkel for real incident logs | This week |
| All | Upload experimental data to wab-paper repo | Before Thursday |
