# 02 — Grill (5 personas, 3 rounds)

Personas: **SMR** Senior ML Researcher · **SRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take
- **SMR:** pass@k is the right upgrade; mean reward isn't comparable across models with
  different variance profiles. But pass@k from a 0.8 threshold on a *continuous* reward
  is a thresholding choice — defend 0.8 or it's arbitrary. Report the mean too so we keep
  the continuous signal.
- **SRE:** For incident response the metric that matters is "did the SLO come back and was
  the root actually fixed, without firing a destructive trap." pass@1 ≈ "fix it on the
  first page" which is exactly the on-call reality. Good. Make sure the threshold encodes
  *no trap fired*, not just reward magnitude.
- **REV:** With 3 seeds your pass@5 is an *extrapolation* (you only drew 3, you can't draw
  5). The unbiased estimator handles n<k by returning ≤1, but a reviewer will say "you
  reported pass@5 from n=3 — that's a model, not a measurement." Mark it as estimated and
  keep n visible in the table.
- **RLE:** Seeds must actually change sampling. REx temperature/seed is threaded
  (`rex_tree(..., seed=s)`), but the *baseline* proposer must also vary or all baseline
  seeds collapse to one point and pass@k is degenerate. Check the proposer temperature.
- **DVO:** A 15-min cap on a multi-hour sweep means partial data. Fine, but the script
  MUST checkpoint or at least cleanly skip remaining models on a wall-budget so we get a
  written result.json even when truncated. Don't leave a half-written file.

## Round 2 — react to another persona BY NAME (genuine disagreement)
- **RLE → SRE:** I disagree that pass@1 alone is "the on-call reality." On-call you *do*
  retry — that's literally what REx is. So pass@2/5 for REx is meaningful, but for the
  *baseline* zero-shot, pass@k>1 means "resample a fresh cold answer," which no human does.
  Comparing baseline-pass@5 to REx-pass@5 risks flattering the baseline. We should headline
  **baseline-pass@1 vs REx-pass@1** and treat higher k as secondary.
- **SRE → RLE:** Partially concede, but pass@k for the baseline is still a legitimate
  *capability ceiling* ("if you let this frozen model try 5 times, how often is one right").
  Keep it, just don't claim it's the headline.
- **REV → SMR:** I push back on "just report mean too keeps the signal." Mean reward on
  this substrate is dominated by partial-credit (0.4 for naming a symptom). A model can
  farm 0.4s and look fine on mean while *never* resolving an incident. That's precisely
  why pass@1 is the honest headline and mean is the misleading one — don't co-headline them.
- **SMR → REV:** Fair. Demote mean to a diagnostic column, not the lead metric.
- **DVO → REV:** Your "pass@5 from n=3 is a model not a measurement" is right but don't
  drop it — drop the *claim*. Print n in every row so the extrapolation is self-evident.

## Round 3 — synthesis
1. **Headline = pass@1** (baseline vs REx), with Wilson 95% CI. pass@2/pass@5 reported as
   secondary, **with n shown** so the n<k extrapolation is transparent.
2. Threshold **0.8 = SLO restored + root cleared + no trap** — this is the existing P0
   definition in `eval_pass_at_k.py`/`compute_pass_at_k.binary_pass`; reuse it verbatim.
3. Keep **mean reward + std** as diagnostic columns (std = trainability spread), not lead.
4. **Baseline proposer must vary across seeds** (temperature > 0) or pass@k is degenerate —
   verify and document.
5. Wall-budget guard that still writes a complete result.json on truncation.
6. Restrict real run to working gateway models (Anthropic-direct is 400/out-of-credits).
