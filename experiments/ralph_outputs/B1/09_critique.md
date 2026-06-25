# B1 — 09 Critique (honest)

## The main weakness — the full grid did NOT run under the cap
B1's literal ask is 1050 episodes; I ran 150 (14%). The other 900 are deferred to an
off-cap command + A1's reference. This is the honest, brief-mandated outcome (cap ~15 min;
full grid ~50 min), but a reviewer can fairly say "you delivered a subset, not the full
grid." Defense: the script IS the full grid (`--per-family 0`), it is resumable, and A1
independently ran the full 42 incidents at 3 seeds — so the full-grid behavior is evidenced,
just not at the full 5-seed depth in one capped window.

## What a reviewer attacks
1. **Subset size / per-family.** n=30/condition overall (fine for the overall headline,
   CI ~±0.16) but n=10/family is too thin for any family-level claim. I explicitly do NOT
   claim per-family results from the subset. Still, the subset's overall pass@1 is itself
   wider than the full grid would give.
2. **Easy-incident bias.** The subset is `sorted(names)[:2]` per family — deterministic and
   non-cherry-picked, but it omits the hardest multi-fault cascades (80-multi-*, 82-multi-*).
   rex's subset cascade pass@1 (0.900) may be optimistic vs the full cascade set; A1's full
   cascade pass@1 was 0.850, so the gap is small but real.
3. **Near-saturation of rex.** rex mean 0.98 / std 0.08 → almost no within-group spread.
   Great for a benchmark demo, BAD as an RL training reward (little gradient). The honest
   reading: this grid measures rex's CEILING, not its trainability. The realistic baselines
   (best_of_n/retry/rex_no_oracle, std 0.25–0.42) are where trainable spread lives.
4. **pass@5 from 5 seeds** is "ever solved" (Chen estimator, k=n) — over-credits; I flag it
   and headline pass@1 only.
5. **Wilson CI iid caveat.** Seeds within an incident share that incident's difficulty, so
   the pooled-Bernoulli CI slightly understates variance. Standard pass@k limitation; same
   convention as the core pipeline and A1.

## Negative / blocked results (stated plainly)
- zero_shot and rex_no_oracle score **0.000 pass@1 on cascade AND novel** in the subset —
  the oracle feedback (rex) is what carries those families. This is a real, unflattering
  result for the baselines and is reported, not hidden.
- The full 1050-episode grid is BLOCKED by the compute cap; not fabricated.

## What's missing
- The full-grid JSON at 5 seeds (deferred / off-cap).
- Multi-model frontier (only glm-5p2 here; `--frontier` exists in core for that).
- Per-incident difficulty breakdown beyond the 6 sampled incidents.
