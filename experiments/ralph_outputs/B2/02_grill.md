# B2 — Step 2: Grill (5 personas, 3 rounds)

Personas: **SR** Senior ML Researcher, **SRE** Principal SRE, **REV** AAAI Reviewer,
**RLE** RL Engineer, **DO** DevOps Lead.

## Round 1 — initial take

**SR:** McNemar is the right test here — the conditions are evaluated on the same
(incident, seed) pairs, so they're paired binary outcomes. Just make sure you use
the *exact* binomial test, not the chi-square approximation, because discordant
counts in the novel family will be tiny (n_disc as low as 1-2). Asymptotic chi-square
is junk at n<25.

**SRE:** I care about decisions, not p-values. If REx beats best-of-N on cascades I
want to know it's not noise before I page someone differently. But a "pass" is a
reward >= 0.8 threshold — that binarization throws away the magnitude. Two conditions
could differ a lot in mean reward yet tie on McNemar.

**REV:** You're running 10 pairs x 4 families x 2 models = 80 tests. If you report any
bare p<0.05 you're p-hacking. I will reject the paper unless you correct for multiple
comparisons. Also: where does the paper currently *claim* McNemar? If it's claimed but
unrun, that's a fabrication risk — this task is essentially auditing the paper's own claim.

**RLE:** The per-incident reward lists are seed-ordered. If condition A's seed order
doesn't match condition B's, the pairing is silently wrong and every number is garbage.
Prove the alignment. Also seeds=3 vs 5 differ between A1 and A2 — don't hardcode.

**DO:** Make it a single dependency-free script I can run in CI on any new result JSON.
No scipy install, no notebook. It should exit non-zero on malformed input so a pipeline
catches it.

## Round 2 — react to another persona (genuine disagreement)

**SR (vs SRE):** I disagree with SRE's framing. The pass/fail binarization is not a bug,
it's the *point* — the paper's headline metric IS pass@k at threshold 0.8. McNemar on
that exact binary is the statistically honest companion to pass@k. If you want magnitude,
that's a different test (paired t / Wilcoxon on rewards), out of scope for B2. Don't
smear the deliverable by testing a different quantity than the paper reports.

**SRE (vs SR):** Fine, but then SR is over-trusting a binary that sits right on a cliff.
Rewards cluster near 0.8. A reward of 0.79 vs 0.81 flips pass/fail on noise. McNemar will
call that a discordant pair as if it were a clean win. SR's "statistically honest" test is
honest about the *wrong* sensitivity. At minimum the tool must let me sweep the threshold.

**REV (vs RLE):** RLE worries about seed alignment — valid — but the bigger threat to
publication is RLE saying "don't hardcode seeds" as if that's the hard part. The hard part
is that with n_disc=1 in novel, the *minimum possible* two-sided exact p is 1.0. You
literally cannot reach significance. Reporting "not significant" there is meaningless, not
a finding. The tool must surface n_disc so readers don't over-read underpowered cells.

**RLE (vs DO):** DO wants CI-fail-on-malformed, but I'd push back: a result JSON that's
missing one condition shouldn't nuke the whole run — sometimes you legitimately have a
subset. Hard-failing is brittle. I'd rather it error clearly per-file and continue. (We
compromise: error+exit on truly broken structure, KeyError surfaced with the missing name.)

**DO (vs REV):** REV's Holm correction is correct but I disagree it should gate the script's
exit code. Significance is a reporting concern, not a pipeline-health concern. The script
should always compute and emit; humans/the paper decide. Don't conflate "test failed to run"
with "result not significant."

## Round 3 — synthesis
- Use **exact** binomial (math.comb), report chi2_cc only as a secondary column. (SR, REV)
- Keep binary pass/fail at the file's own threshold — it matches pass@k — but expose a
  `--threshold` override so the cliff-sensitivity worry (SRE) is testable. (SR + SRE compromise)
- **Always** report `n_discordant`; flag underpowered cells implicitly (a reader sees disc=1).
  Apply **Holm-Bonferroni** across the pairwise family and report raw vs corrected separately. (REV)
- Read `seeds`, `threshold`, conditions, and family map from the file; never hardcode. Prove
  alignment with a unit test on a known synthetic. (RLE)
- Single stdlib script; exit 2 on structurally broken input, but significance never affects
  exit code. (DO + RLE + DO/REV compromise)
- Scope: paired binary (pass@k companion) only. Magnitude tests are explicitly out of scope. (SR)
