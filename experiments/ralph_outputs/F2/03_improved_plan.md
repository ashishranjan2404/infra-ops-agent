# F2 — 03 Improved Plan (post-grill)

## What changed vs 01_plan
The grill restructured the section from "synthetic / single-domain / preliminary RFT"
into **six grounded themes**, with sharper scoping.

### Accepted critiques
- **PSRE — split author-circularity out** from generic "synthetic data." The same
  authorship of the incident generator *and* the deterministic judge is its own
  limitation (oracle circularity), not a sub-clause. → New dedicated subsection L2.
- **REV — no "we didn't observe it" comfort** on reward hacking. The D13 hack is
  disclosed as a *real, measured* fragility (5 exploit classes, hedge 92.9%), framed by
  the 0.30 reward cap as *scope* not exoneration. → L4 rewritten.
- **DEV — distinguish weak-evidence from absent-evidence.** Claim 2 (Fireball transfer)
  is BLOCKED/unsubstantiated in-repo (P7), not merely weak. → L5 says this explicitly.
- **RLE — RFT is preliminary, not "learning."** +0.037 over 15 steps, N=10 tasks, no
  held-out curve, movement within seed band. → L3 states it as directional, not
  established.
- **REV/RLE — statistical power.** Single-model diagrams, 4 indistinguishable ablation
  conditions (0.23–0.25), missing CIs on headline lifts. → L6.

### Rejected critiques (and why)
- **SMR's pushback against PSRE's "circularity = worthless":** accepted the *correction*,
  rejected the *strong form*. We do NOT claim oracle-defined metrics are worthless (that
  would invalidate SWE-bench/AIOpsLab too). We scope it: fool-rate and pass@k are
  relative to an author oracle; blind/external incidents are the fix. (D13 itself makes
  this caveat.)
- **RLE's "reward hack is overstated":** partially rejected per REV. We keep the full
  measured severity (92.9% hedge fool-rate is real) and do not soften it with
  "unproven reachability under RL" as if that excuses it — we list reachability as an
  open question, not a defense.

## Final section structure
- L1 Synthetic incident data
- L2 Oracle circularity (generator ⇄ judge authorship)
- L3 Preliminary reinforcement fine-tuning
- L4 Reward-function fragility / reward hacking (D13)
- L5 Single-domain + unsubstantiated cross-domain transfer
- L6 Statistical power, single-model evaluation, reproducibility gaps
- A closing "what this does NOT invalidate" paragraph (keeps the section from reading
  as self-defeating — SMR's scoping discipline).

## Success criteria (unchanged + tightened)
- ≥6 grounded limitations, each with a file/number citation.
- Closing paragraph scopes what survives.
- `check_limitations.py` confirms every cited path exists.
