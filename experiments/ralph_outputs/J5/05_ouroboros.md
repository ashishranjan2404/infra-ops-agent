# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Reliability / harness engineer
**Problems found:**
1. The judge is deterministic keyword-matching. If the agent's stated root cause
   *happens* to contain "waf"/"regex"/"rollback" tokens it scores diagnosis-correct
   even with shallow reasoning. The case study must not over-claim "the agent
   reasoned" — it must quote the sentence and let the reader judge.
2. `_resolved()` only checks `error_rate_pct`/`p99_latency_ms`. If the spec's SLO
   used an unsupported metric the run would vacuously "resolve." → Verify the spec's
   SLO metric is `error_rate_pct` (it is). Note this in test results.
3. The fallback path and the live path produce *different JSON shapes*
   (`steps`/`result` vs `trap`/`fix`). A downstream reader/CASE_STUDY must branch on
   `mode`. → Documented; CASE_STUDY only consumes the realized live shape, with the
   trap branch coming from the separate `trap_vs_fix.json` (single shape).

## Engineer B — ML / eval engineer
**Problems found:**
1. Single LLM sample → not reproducible verbatim. Mitigation: the *grading* is
   deterministic; report the run as one realized trace and pin model + judge mode.
   Do NOT present iter counts as a metric.
2. Proposer swapped from haiku→gpt-5.5 because of credit exhaustion. That changes
   "the agent." The case study must disclose the model actually used, not imply the
   default roster model. → Disclosed prominently.
3. `best_iter=1` but budget=6: the loop stopped early on the clean win (correct —
   `failed_checks` empty breaks the loop). Make sure the narrative doesn't imply the
   agent "used 6 tries." → It used 2.

## Engineer C — Skeptical staff reviewer
**Problems found:**
1. "Trap avoided" is ambiguous: the *agent never proposed* the trap, AND the
   *harness would block it*. These are two different claims. The honest version:
   the agent independently avoided the trap (never proposed scaling the victim),
   and *separately* we demonstrate the harness would have blocked it anyway. Don't
   conflate. → CASE_STUDY states both, separately.
2. The cascade prompt literally hints "it may be UPSTREAM... ALL products are
   failing simultaneously through a shared path." That's a strong nudge. A reviewer
   will say the diagnosis was spoon-fed. → Acknowledge the hint explicitly in the
   "limitations" section; credit the agent only for *using* it correctly, not for
   discovering upstreamness unaided.
3. N=1. Already scoped, but C wants it in the FIRST paragraph, not buried.

## Final filtered spec (changes folded in)
- CASE_STUDY discloses model (gpt-5.5), judge mode (deterministic), seed (1076),
  and the haiku→gateway swap **up front**.
- "Trap avoided" split into two explicit claims (agent-never-proposed +
  harness-would-block), with the trap demonstration from `trap_vs_fix.json`.
- A **Limitations** section: N=1, prompt contains an upstream hint, deterministic
  keyword judge, single sample, by-construction reward for the trap branch.
- Narrative quotes the agent's stated root cause and feedback strings verbatim and
  says "2 iterations," not 6.
