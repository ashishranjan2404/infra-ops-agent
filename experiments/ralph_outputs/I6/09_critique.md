# I6 — 09 Critique (honest)

## What's weak
1. **Small N.** 57 rollouts (12 probe + 45 unique HUD) is error-analysis enumeration, not
   a distribution with statistical power. The 61% `no_fix` figure is dominated by ONE
   scenario (singleton_node_notready, 20 rollouts all `no_fix`). Drop that scenario and
   the picture changes completely. Reported with a caveat, but a reviewer will still note
   the corpus is unbalanced by scenario.
2. **HUD scores are re-derived, not recorded.** The original trace doesn't store the reward
   response, so the entire HUD column rests on the assertion that our replay == the
   original scoring path. The replay-trap unit test supports this, but there is no
   byte-for-byte ground truth to compare against. A skeptic can say "you re-graded with
   today's scoring code, not the code that produced the trace."
3. **`no_fix` conflates two very different things.** (a) The model abstained safely on an
   unfixable scenario (singleton node — correct behavior, penalized by reward), and (b) the
   model just forgot the remediation. Both land in `no_fix`. I added `safe_abstain` to
   separate them, but only 1 HUD row was a known-empty plan; the probe rows lack action
   counts so their abstain-vs-forgot status is ambiguous.
4. **No `timeout` bucket** even though the task named it. Defensible (REx is single-shot,
   no wall clock), and documented — but it's a deviation from the literal ask.
5. **Curriculum/frontier aggregate scores unused as per-rollout records.** They have no
   per-episode `failed_checks`, so I deliberately left them out; that's defensible but
   leaves cell-level reward data on the table.

## What a reviewer attacks first
- "Your headline is an artifact of scenario imbalance." → True; mitigated only by the
  by-scenario breakdown, which a careful reader must consult.
- "Re-grading proves nothing about the original rollout's reward." → Partially fair; the
  scoring code is deterministic and version-stable, but I can't fully refute it.

## What's missing
- A baseline-vs-rex split of the failure buckets (does REx refinement convert `trap_taken`
  → `clean_win`? The data suggests yes for oom_kill, but I didn't formally pair them).
- Per-model breakdown (haiku vs opus vs gpt) — the HUD traces don't reliably carry the
  model id in the score_plan payload, so I couldn't slice by model.

## Honest verdict
Deliverable is real and runnable; the failure taxonomy is correct and useful for
prioritizing reward/curriculum work (it cleanly surfaces the safe-abstain-penalized mode
and the oom trap mode). The numbers are directional, not statistical, and the report says so.
