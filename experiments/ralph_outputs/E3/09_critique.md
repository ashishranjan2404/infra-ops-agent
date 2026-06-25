# E3 — 09 Critique (honest)

## What a reviewer attacks
1. **It's really a 2-way comparison.** The headline "3-way" is structurally a 2-arm run plus a
   blocked annotation. Honest, but a skeptic will say the third arm is vaporware. Mitigation: the
   blocker is upstream and real (E2/D8 produced nothing), and we refused to fake it — which is the
   correct behavior, but it does mean the *central* claim of the task can't be answered yet.
2. **Underpowered.** 14 incidents × 2 seeds = 28 trials/arm. The +0.036 pass@1 lift for OpenSRE is
   well inside overlapping Wilson CIs — statistically indistinguishable from zero. We do not claim
   significance, but the result is weak by design (the OpenSRE checkpoint was known-flat).
3. **Reasoning-model parse cap.** `Qwen/Qwen3-8B` emits `<think>...` and `parse_plan` may extract a
   degenerate plan, depressing both arms' rewards. This is symmetric (doesn't bias the comparison)
   but compresses the measurable gap — a stronger lift could be masked. A `<think>`-aware parser
   would be a fairer test; out of scope here (no shared-file edits).
4. **Checkpoint trust.** A 200 from `opensre-qwen3-8b-1e439a` proves the slug is *served*, not that
   it's the specific GRPO checkpoint we believe. We record the exact `model` string for audit but
   cannot verify checkpoint identity from the eval side.
5. **Serving parity.** Base vs forked slug may use different gateway sampling defaults; not fully
   controllable here. Documented as a caveat, not eliminated.
6. **pass@2 at seeds=2** is near-degenerate; we lead with pass@1 and mean to avoid over-reading it.

## What's weak / missing
- No statistical test (intentional — the model is flat and n is small); only descriptive stats.
- Only the 8B OpenSRE fork was run; the 30B fork (`opensre-qwen3-30b`) is reachable too and could be
  added as a 4th column for a stronger trained arm — left as an obvious extension.
- The Fireball arm blocks the *thesis* of the task. Until an E2/D8 Fireball dataset + fork exists,
  this comparison stays incomplete on its most important axis.

## What's solid
- Reuses the repo's validated deterministic judge and stats — reproducible, no LLM-judge noise.
- Real run, 0 errors, honest null-ish result with a verified headroom check (no floor artifact).
- Zero fabricated numbers; strict no-shared-core-edit compliance; clean, tested, namespaced artifacts.

## Honest bottom line
The harness and the runnable comparison are real and correct. The *scientific* answer ("does
Fireball training beat OpenSRE and zero-shot on cascades?") is **blocked** on the missing Fireball
model, and the OpenSRE-vs-zero-shot signal is **small and not significant** — exactly what the prior
flat-training evidence predicted.
