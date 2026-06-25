# J7 — 09 Critique (honest)

## What a reviewer attacks

1. **Action-selection ≠ incident resolution.** The strongest critique: this runner scores
   whether the agent *names* the right runbook command, not whether applying it actually
   drives the metric back under SLO. The bench's real value is that live recovery chain,
   and it did NOT run. The gcp prior results show this gap is real (scenarios with
   `action_fired=true` but `recovered=false`). I label the metric `action_select_accuracy`
   and keep it separate from `reward`, but the headline "agent run against the bench" is,
   honestly, "agent run against an *offline projection* of the bench."

2. **The menu leaks.** Gold fixes appear verbatim and contain the service name that's also
   in the prompt. The 0.867 baseline is inflated by lexical overlap, not reasoning. A
   leak-free design (free-form command generation graded by the cluster) is exactly what
   the blocker prevents. So the dry-run number is a floor/sanity check, not a capability
   claim.

3. **The live LLM result is weak and partly an artifact.** minimax-m3 scored 0.2, but most
   misses were empty completions because the model is served on a base-completion endpoint
   that ignores the chat `system` prompt — a harness/provider mismatch, not (only) a model
   failure. A fair live number needs a chat model (the Anthropic/gateway path), which was
   blocked on credits. So I have **no clean strong-model live number**.

4. **No comparison across the roster.** A real eval would sweep several models and report
   spread (HUD doctrine). I ran one working live model; the rest were credit-gated. Single
   data point.

## What's weak / missing
- No live recovery scoring (the blocker).
- No multi-model spread; no chat-model live run.
- Baseline-leakage caveat is disclosed but not *quantified* (e.g., ablating the service
  name from the prompt to measure leakage contribution) — I didn't run that ablation.
- The integration into `stages/06_run_scenario.sh` is described, not wired (no-core-edit
  rule), so it's unproven end-to-end against a cluster.

## What's genuinely solid
- The blocker is real, exact, and correctly refused (no personal-account workaround, no
  cost). This is the honest, correct outcome for a no-cost run.
- The runner is real, runnable, deterministic, tested, and cloud-free by construction.
- It produces actual LLM output and scores it — the agent IS pointed at the bench
  scenarios, end-to-end, just stopping short of the (impossible) cloud apply.

## Bottom line
A correct, tested, reusable harness + a precisely-documented live-cloud blocker — which
the brief explicitly prefers over fabricated live numbers. The capability claim is
deliberately modest and the gaps are named, not hidden.
