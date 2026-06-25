# A1 — 02 Grill (5 personas × 3 rounds)

Personas: **SML** (Senior ML Researcher), **PSRE** (Principal SRE), **REV** (AAAI Reviewer),
**RLE** (RL Engineer), **DEV** (DevOps Lead).

## Round 1 — initial take
- **SML**: Going from 15 → 42 incidents is a strictly better evaluation: more incidents
  shrinks the binomial variance on pass@1 and makes the per-family CIs publishable. But
  pass@2/pass@5 with only 3 seeds are *extrapolations* of the Chen estimator beyond n; we
  must label them as estimates and prefer pass@1 with its Wilson CI as the headline.
- **PSRE**: The thing I care about is that the floor check holds on ALL 42, not just the 15
  we used to run. A benchmark where the trap or the empty plan can pass is worthless. Show me
  `floor_ok` over the whole set before any pass@k number.
- **REV**: "Full 42" must mean *all* of simple/cascade/novel, not 14-per-family truncation.
  And the judge must be deterministic — if the reward came from an LLM judge, the metric is
  not reproducible and I'd reject. Confirm the deterministic P0 judge path.
- **RLE**: The within-group reward **std** per incident is the real prize — it's the unit of
  trainability. With 3 seeds the per-incident std is noisy; report the family-level std which
  pools more samples. Also: are the 42 incidents trivially saturated (all pass) or all-zero?
  Either kills spread.
- **DEV**: 3.5k LLM calls at ~7 s each will not finish in a tight Ralph budget on 8 workers.
  We need checkpoint/resume and a fallback to fewer conditions, and we must NOT write into a
  shared results dir that another worker is also touching.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SML**: I disagree with SML treating pass@5 as merely "label as estimate." With only
  3 seeds, `pass_at_k(n=3,c,5)` returns 1.0 whenever `n-c<k`, i.e. it *saturates to 1.0* for
  any incident the model ever solves. That's not a soft estimate, it's a degenerate value.
  Either bump seeds to ≥5 so pass@5 is meaningful, or DROP pass@5 from the headline entirely.
- **PSRE → DEV**: I push back on DEV's "drop to fewer conditions to fit budget." If we drop
  `rex` we lose the entire thesis (REx beats baseline). I'd rather drop SEEDS than drop the
  `rex` condition. Full incident coverage on `zero_shot`+`rex` at lower seeds beats a partial
  incident sweep on all 5 conditions.
- **REV → RLE**: RLE wants family-level std, but a family-level std *mixes* incidents of
  different difficulty and can look healthy while every individual incident is degenerate
  (all-0 or all-1). I want the **per-incident** reward vectors retained in the JSON
  (`per_incident_rewards`) so a reviewer can audit spread incident-by-incident. Good news:
  the existing pipeline already stores `per_incident_rewards` — keep it.
- **SML → REV**: Fair on reproducibility, but I'll note the *proposer* is intentionally
  stochastic (temp 0.7) — that's the source of pass@k variance and is correct. Only the judge
  must be deterministic. We are not claiming the proposer is deterministic.
- **DEV → PSRE**: Conceding the priority order (keep `rex`, cut seeds), but I insist on
  writing the checkpoint to the task-namespaced artifacts dir, because the shared
  `experiments/results/` already has a half-finished `ablation_pass_at_k_glm-5p2.json.partial`
  from another run and we must not clobber it.

## Round 3 — synthesis
1. "Full" = all 42 incidents (12/20/10) via `per_family=None`. Verify the count == 42.
2. Run floor_check over all 42 FIRST and require `floor_ok` before reporting pass@k.
3. Headline metric = **pass@1 with Wilson 95% CI**, per family. pass@2/pass@5 reported but
   flagged: with seeds=3 pass@5 is degenerate (saturates), so prioritize seeds and treat
   pass@5 as upper-bound-y. If budget allows, run seeds≥5 for a clean pass@5.
4. Priority under budget pressure: keep both anchor conditions (`zero_shot`, `rex`) at full
   42-incident coverage; only then add the other three conditions / more seeds.
5. Use the deterministic P0 judge (already the default in `_score`). Retain
   `per_incident_rewards` for auditability. Report family-level reward std.
6. Parallel safety: checkpoint + final JSON go to `A1/artifacts/`, never the shared dir;
   import the core pipeline unmodified.
