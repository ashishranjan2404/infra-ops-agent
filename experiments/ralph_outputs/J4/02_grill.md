# J4 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial takes
- **SMR**: MTTR is right-skewed and heavy-tailed. Do NOT report a difference of
  arithmetic means — one Roblox-scale outage dominates everything. Work in log
  space; the effect of interest is a *multiplicative* speedup. Report a ratio of
  geometric means with a bootstrap CI, and a paired test where possible.
- **PSRE**: MTTR is not one number. There's TTD (detect), TTA (acknowledge), TTR
  (resolve), and the agent mostly helps the *diagnosis* segment, not deploy/rollback
  latency. If you measure end-to-end wall clock you'll dilute a real effect with
  fixed overhead the agent can't touch. Also: which incidents? A cert-expiry is a
  90-second fix; a BGP withdrawal is hours. Stratify by severity.
- **REV**: What's the unit of analysis and where does randomization happen? If the
  same operator does both arms, you have order/learning confounds and pseudo-
  replication. State the design explicitly. n=18 real labels is not a study.
- **RLE**: The "agent" must be a fixed, versioned policy or the measurement isn't
  reproducible. Define the intervention precisely: which model, which tools, which
  prompt, frozen. Otherwise speedup is unattributable.
- **DOL**: You will never get clean A/B in production on-call — you can't withhold
  a helpful tool from real customer-impacting incidents (ethics + SLA). The only
  honest path is a *replayed/staged* incident lab. Say so.

## Round 2 — react to ANOTHER persona by name (genuine disagreement)
- **PSRE vs SMR**: "Geometric mean is mathematically tidy but operationally
  meaningless to my VP — nobody budgets in log-minutes. I want the *median*
  minutes saved and the % of incidents resolved inside the SLO budget. Your GM
  ratio hides that a 2x on a 4-minute incident is irrelevant while a 2x on a
  3-hour incident is the whole ballgame." → Tension: scale-free effect vs
  business-relevant absolute minutes.
- **REV vs DOL**: "If you concede you can only run staged replays, then your
  external validity is gone — you're measuring agent help on *known, scripted*
  incidents, which is exactly where an LLM looks best. That's a contaminated
  benchmark. I'd reject a paper that claims production MTTR improvement from a
  scripted lab." → Sharp disagreement on whether staged data can support the claim.
- **RLE vs PSRE**: "You want to stratify by severity AND segment TTD/TTA/TTR AND
  match operators — with n in the dozens you'll have one incident per cell and
  zero power. Pick the *one* segment the agent touches (diagnosis-to-fix) and
  measure that cleanly; don't death-by-stratification." → Power vs granularity.
- **SMR vs REV**: "n=18 isn't the study — agreed — but that's why I'm proposing a
  *within-subjects replay* with bootstrap, which gets usable power at n≈30–40
  pairs. Your between-subjects purity demand would need 100+ incidents we don't have."
- **DOL vs RLE**: "Freezing the model is necessary but not sufficient — operator
  skill variance will dwarf model version. You need operator as a random effect or
  matched pairs, or your 'agent speedup' is just which engineers got assigned."

## Round 3 — synthesis
Consensus reached:
1. **Endpoint**: primary = multiplicative speedup (GM ratio) in log space (SMR);
   report median absolute minutes + %-within-SLO as **secondary** so it's
   business-legible (PSRE). Both, not one.
2. **Design**: default to **within-subjects replay** for power (SMR/RLE), but the
   harness must also support **between-subjects A/B** (REV) — implement both.
3. **Segment**: measure diagnosis-to-resolution where the agent acts; don't dilute
   with fixed deploy overhead, and don't over-stratify (RLE/PSRE compromise).
4. **Confounds**: operator as random effect / matched pairs; freeze the agent
   policy (RLE/DOL).
5. **Honesty**: staged-replay external-validity limit is real (REV/DOL) — must be
   stated as a first-class limitation, and real data collection flagged as the blocker.
