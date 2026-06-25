# G3 — 09 Critique (honest)

## What a reviewer will attack
1. **Ordinal merge of incomparable benchmarks.** The single biggest objection: ranking a
   sim-pass@1 against live-K8s-E2E is methodologically dubious. We mitigate (banner,
   regime column, no "win" claim) but do not eliminate it — the table can still be
   screenshotted out of context. This is inherent to the task framing ("where would we
   rank") and is the honest limitation, not a bug we can fix.
2. **SREGym numbers are transcribed, not reproduced.** We did not run SREGym (external
   benchmark, no install/cluster here). If the cited leaderboard shifts or a number was
   mis-transcribed, our rank moves. The values are frozen + cited for auditability, but
   this is a real trust dependency.
3. **No cross-benchmark significance test.** We can't say our 34.9% is *significantly*
   above Kimi's 32.9% — we lack SREGym per-problem outcomes. The "rank 8" is an ordinal
   placement of point estimates only; the Kimi rows are within plausible noise of us.
4. **Model confound.** Our cheaper models (glm-5p2 / deepseek-v4-pro) vs SREGym's frontier
   Sonnet-4.6 / GPT-5.4 means the deficit could be entirely model, not method. We cannot
   separate the two without a matched-model run (blocked: API budget).
5. **Grader leniency.** reward@0.8 is plausibly easier than verified live recovery, which
   could *flatter* our fair band. So our true fair rank might be even lower.
6. **Overlap with B15.** A reviewer may say G3 is a thin re-skin of B15. Rebuttal: G3 adds
   the explicit ordinal-rank artifact and the "rank 8/13" answer B15 deliberately avoided
   (B15 framed as no-ranking comparison). Different deliverable, shared cited inputs.

## What's weak / missing
- No machine-readable (JSON) ranked output — only markdown.
- Family<->partition mapping is illustrative, not registered.
- Single headline model (A1/glm-5p2); A2 cross-check is in prose, not the table.

## Blocked (honest, not faked)
- **Matched-model, matched-substrate head-to-head** (run our agent on SREGym, or a
  frontier model on our sim) — needs SREGym infra + API budget. This is the only way to
  turn "positioning" into a real comparison. Documented; not fabricated.

## Net honest assessment
A correct, validated, self-contained positioning artifact with a defensible-but-caveated
answer. Its conclusions (bottom-of-board on fair terms; REx out-of-regime) are robust to
the A1/A2 model swap. Its ceiling is bounded by the fundamental non-equivalence of the two
benchmarks, which we surface rather than hide.
