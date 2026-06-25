# 02 — Grill (5 personas, 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DEVOPS).

## Round 1 — initial takes

**SMR:** Sweeping the threshold is the right robustness check. The real question a
reviewer asks is "did you pick 0.80 because REx happened to win there?" Re-binarising
fixed reward data at multiple cutoffs answers that with zero new compute. Good.

**PSRE:** From an ops standpoint the cutoff IS the SLA gate. 0.80 means "diagnosis +
fix + resolved minus partials." A threshold sweep is basically a sensitivity analysis
on the SLA. I want to see whether REx's win survives a STRICTER gate (0.90), because
in prod we care about the strict end, not the lenient end.

**AAAI:** A robustness table is necessary but not sufficient. With n=15 per arm the
Wilson intervals will overlap massively. Do not claim "significant at every
threshold." Claim "rank-order preserved." Also: a sweep over a monotone transform of
ONE reward distribution can be trivially robust or trivially fragile depending on
where the mass sits — show the reward histogram intuition, not just the table.

**RLE:** Note the reward is not continuous-uniform — it lands on a few discrete bands
(0.0, 0.25, 0.3, 0.4, 0.7, 1.0) because it's a weighted sum of mostly-binary terms.
So thresholds 0.80/0.86/0.90 may give IDENTICAL pass-rates (nothing lands between
0.70 and 1.0 except 0.7). The sweep's discriminating cut is really 0.70 vs >0.70.
That's fine but say it out loud or the table looks suspiciously flat.

**DEVOPS:** Make it a standalone script that doesn't import the shared modules — if
it imports `rex.eval_pass_at_k` it'll drag in `agent.llm` and need network/keys.
Copy the 10 lines of estimator. Reproducibility > DRY here.

## Round 2 — react to another persona (genuine disagreement)

**RLE → AAAI:** I disagree that the histogram is "necessary." The discreteness of the
reward is the WHOLE story — once you state the reward bands, the table is
self-explaining and a histogram is decoration. Adding a plot is over-engineering for
a 15-point dataset. The table + the band list is the honest artifact.

**AAAI → RLE:** Partly conceding, but you're underselling the risk. If 0.80/0.86/0.90
give identical numbers, a skeptical reviewer says "you padded the sweep with three
redundant thresholds to look thorough." That's WORSE than two thresholds. The fix
isn't a histogram — it's to *report* the redundancy explicitly and keep 0.86/0.90 as
deliberate "does the strict end break it" checks, with a sentence saying why.

**PSRE → DEVOPS:** I push back on "reproducibility > DRY." Copy-pasting `binary_pass`
risks the artifact silently drifting from the real `compute_pass_at_k.binary_pass` if
core changes. At minimum add a test that the copied estimator matches the canonical
one on a few values. Otherwise the robustness claim rests on a fork that could rot.

**DEVOPS → PSRE:** Fair — I'll concede a guard. But I won't import at runtime (network
risk). Compromise: a tiny offline equivalence check in the test step comparing the
copied `binary_pass`/`wilson_ci` against hand-computed values from the canonical
formula. Pins correctness without the import.

**SMR → PSRE:** On "only the strict end matters" — disagree. Showing the gap WIDENS
from +0.20 at 0.70 to +0.33 at 0.80+ is the strongest possible evidence: REx isn't
just clearing a low bar, it's the only arm that ever reaches the high reward band.
The lenient end is informative precisely because it shows the controls catch up there.

## Round 3 — synthesis

Consensus:
1. Keep all four thresholds; 0.86/0.90 are deliberate strict-end stress points.
2. EXPECT (and state) that the reward is discrete-banded, so several thresholds may
   tie — report that as a finding, not hide it.
3. Standalone script, no shared imports; add an offline equivalence check for the
   copied estimators (PSRE/DEVOPS compromise) in the test step.
4. Report Wilson CIs; claim "rank-order / gap preserved," NOT statistical separation
   (AAAI). n=15 is the honest limitation.
5. Headline framing: report the GAP per threshold; widening gap is the real result.
