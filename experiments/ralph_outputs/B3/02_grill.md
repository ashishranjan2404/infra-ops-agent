# B3 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR**: Wilson is the right interval for these tables — Wald would report a width-0
"CI" for the cascade cells at p=0.02 and the rex novel cells at p=1.0, which is
statistically dishonest. Make sure the unit test pins exact textbook values, not just
"runs without crashing." 50/100 → [0.4038, 0.5962] is the canonical check.

**PSRE**: My concern is operational meaning. pass@1 = 0.02 with n=50 — the CI [0.004,
0.105] tells the on-call reader "this could be anywhere up to 10%." That's the whole
point: a point estimate of 2% with no interval looks like "basically never," but the
upper bound matters for SLO risk. Good. But are the n's per *cell* real, or pooled
across families in a way that double-counts? Verify n adds up.

**REV**: I will reject any paper that reports pass@k without intervals, so this is
necessary. But independence: pass@k draws within an incident across seeds are NOT
independent (same scenario, correlated). A binomial Wilson interval assumes iid
Bernoulli. You are understating uncertainty. State this limitation explicitly or I
ding you.

**RLE**: Practically, I just want the tool to read the A1/A2 JSONs that already exist
and not re-run any expensive eval. Recomputing CIs from stored (n, passes) is cheap and
deterministic. Don't re-invoke the model. Also: cross-check against the `ci95` already
stored upstream so we know we didn't fat-finger the formula.

**DOL**: Make it a single self-contained script, stdlib only, no edits to shared files,
runnable as `python3 wilson_ci.py`. Parallel-safe. Emit both human table and JSON so a
downstream chart job can consume it. Don't add scipy as a dependency for one z-quantile.

## Round 2 — react to another persona (genuine disagreement)

**REV → SMR**: You called the binomial Wilson interval "right." I disagree on framing.
It's the right *interval family*, but applied to correlated seed draws it is
*anticonservative* — the true 95% interval is WIDER. Don't oversell "honest." It's
"honest about binomial sampling error, blind to seed correlation." Those are different.

**SMR → REV**: Partially concede, but you're overreaching. The dominant variance source
here is incident-to-incident heterogeneity, and the table reports per-family pooled
cells precisely to average that out. A cluster-robust interval would be better but needs
the raw per-incident-per-seed booleans, which the summary JSON doesn't fully expose for
every cell. Within the data we HAVE, binomial Wilson is the defensible choice. I reject
"don't call it honest" — I'll call it "honest within the binomial model" and move on.

**PSRE → DOL**: You said "no scipy for one z-quantile" — agreed, but don't hardcode 1.96
and call it 95%. The two differ in the 3rd decimal and someone will diff against scipy
and file a bug. Use the exact quantile 1.959963984540054. Cheap correctness.

**DOL → RLE**: You want "just read the JSONs." Fine, but auto-discovery that hardcodes
two filenames is brittle. At minimum accept explicit paths on argv so the same tool
works when A3/A4 land. I reject a fully-hardcoded reader.

**RLE → PSRE**: You worry the n's might double-count across families. They don't —
overall n (126 / 150) = sum of family n's (36+60+30 / 50+50+50). But I accept your
push: the tool should *report* n per cell so a reader can verify the arithmetic, not
hide it.

## Round 3 — synthesis

Consensus:
1. Wilson score interval, exact z = 1.959963984540054 (PSRE/DOL).
2. Unit test pins **known** values (50/100, 0/10, 10/10) + symmetry + bounds (SMR).
3. Read the existing A1/A2 JSONs, recompute from stored (n, passes), **cross-check vs
   upstream `ci95`** within 0.01 (RLE).
4. Report n per cell so arithmetic is auditable (PSRE/RLE).
5. Accept explicit argv paths, not only hardcoded discovery (DOL).
6. **Explicitly document** the binomial-iid limitation: intervals capture sampling
   error under a binomial model and are anticonservative w.r.t. seed correlation (REV/SMR).
7. stdlib only, self-contained, no shared-file edits, emit table + JSON (DOL).
