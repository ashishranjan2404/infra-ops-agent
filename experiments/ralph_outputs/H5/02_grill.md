# H5 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (REV)**, **RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take
- **SMR:** A "promotion gate" is just a decision rule over pass@k. Fine, but the gate
  must be defensible: a single point estimate of pass@1 is not enough — you need the CI
  lower bound, or you'll promote noise. Use the CI_lo as a hard requirement.
- **PSRE:** I don't care about pass@1 in the abstract; I care whether the candidate beats
  what we already ship. Gate on **lift over baseline**, per model, or every model with a
  high floor looks "great" regardless of method.
- **REV:** A dashboard is not a contribution. What makes it credible is that the numbers
  trace back to real runs with N and seeds shown. Bury the provenance in the manifest and
  surface it in the UI, or this is decoration.
- **RLE:** Keep the manifest schema stable and versioned. If the HTML hardcodes A1's key
  names it'll break the moment A3 uses a different field. Normalize at generation time.
- **DOL:** "Live monitoring" implies it refreshes. A static file opened via `file://`
  can't even fetch its own JSON in Chrome. Either you embed the data or you ship a serve
  command. Don't hand me something that silently shows nothing.

## Round 2 — react to another persona BY NAME (genuine disagreement)
- **PSRE → SMR:** I disagree that CI_lo should be a *hard* gate. With N=30 incidents the
  CI is wide; you'll reject good candidates on small samples. CI_lo is a *tiebreaker*, not
  a veto. — **SMR rebuts:** No. If CI_lo is below your promote line, you literally cannot
  claim the candidate clears the bar at 95% confidence. Wide CI is exactly when you should
  NOT auto-promote. Keep it a hard requirement; if you want more power, run more seeds.
- **REV → DOL:** "Embed the data" is the wrong call — embedding freezes the manifest into
  the HTML and destroys the whole point of a *live* manifest you regenerate. The fetch +
  file-picker fallback is the correct design; don't conflate convenience with correctness.
  — **DOL concedes** the fallback but insists the failure must be *loud* with instructions,
  not a blank page.
- **RLE → PSRE:** Lift-over-baseline alone is gameable — a model with a terrible baseline
  shows huge lift for a mediocre method. You need an absolute pass@1 floor too. PSRE
  pushes back that absolute floors penalize hard task mixes; **synthesis:** require BOTH
  (absolute pass@1 AND lift), which is what kills the disagreement.
- **SMR → REV:** Provenance in the UI is nice but secondary; the real risk is **selection
  bias** — if the manifest only contains the conditions that won, the gate looks perfect.
  REV agrees this is the sharper objection: include ALL conditions (zero_shot, baselines,
  ablations), not just REx.

## Round 3 — synthesis
Consensus gate = **AND of three tests**: (1) absolute `pass@1 >= 0.80`,
(2) `CI_lo >= 0.70` (robustness, hard requirement per SMR), (3) `lift over same-model
zero_shot >= 0.20` (per PSRE/RLE). Fail (3) → REJECT; otherwise → HOLD. Manifest must
carry **all** conditions per model (anti-selection-bias, SMR/REV) with N, seeds, and
source provenance. HTML must **fetch** the live manifest, fail **loudly** with a serve
hint, and offer a file-picker fallback for `file://` (DOL/REV).
