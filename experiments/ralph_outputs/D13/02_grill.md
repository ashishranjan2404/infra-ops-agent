# D13 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **SRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DEV** DevOps Lead.

## Round 1 — initial takes
- **SMR:** A keyword-overlap judge is a textbook proxy-reward. The interesting
  question for the paper is not "can it be fooled in the abstract" — of course it can —
  but "would GRPO on a frozen Claude policy actually *discover* the exploit within the
  candidate budget?" Measure fool-rate per attack *and* note exploit reachability.
- **SRE:** From an ops view the dangerous failure is the inverse: a model that hedges
  ("could be memory, could be scaling, could be cache") getting graded CORRECT. That's
  exactly the behavior we want to punish in an incident commander. Test the hedge.
- **REV:** "We tested reward hacking" is a claim reviewers will reject unless you have
  (a) a human-oracle baseline disagreeing with the judge and (b) a fool-rate over the
  *full* taskset, not a cherry-picked example. Also state exploitability honestly.
- **RLE:** The reward is 30% diagnosis + 25% fix + 45% resolved. Diagnosis hacking
  alone caps at 0.30. The real danger is hedge-diagnosis (0.30) + a correct fix (0.25)
  with no understanding -> 0.55 reward for a shotgun. Probe the *composed* score.
- **DEV:** Whatever you build must run with zero external deps and not touch core
  files — many workers run in parallel. Self-contained probe + its own results file.

## Round 2 — forced disagreement (react by name)
- **SRE → SMR:** I disagree with SMR's "is it reachable" framing as the *primary*
  lens. A judge vulnerability is a vulnerability whether or not THIS policy finds it;
  a future stronger policy or a prompt leak will. Report the vuln as a vuln. Reachability
  is a *secondary* caveat, not a reason to downgrade the finding.
- **SMR → SRE:** Fair, but I push back the other way: if we don't caveat reachability
  the paper overclaims. The verbatim-gold-echo "attack" is the trap — gold text is
  hidden at eval, so echoing it is impossible for the policy. If we list it as a fooled
  case we mislead. It must be explicitly marked informational/capability-gated.
- **REV → RLE:** RLE's 0.55 composed score is the headline, but I challenge the
  human-oracle for the hedge: is a hedge *really* wrong? Some rubrics reward listing
  the correct hypothesis among others. — **RLE → REV:** No. The scenario design
  explicitly treats the herrings as WRONG mechanisms and penalizes trap actions tied
  to them. A diagnosis that asserts the gold AND the herrings as co-equal is not a
  partial credit case; it is non-committal and would lead an operator to the trap fix.
  Human-oracle = WRONG stands, and I'll document the rationale inline.
- **DEV → SMR:** SMR wants reachability analysis via an actual RL run — I object on
  scope/safety grounds: spinning a training run is hours of GPU and risks the shared
  cluster. A static adversarial probe is the right deliverable; reachability is a
  documented limitation, not a build target.

## Round 3 — synthesis
Consensus: (1) Ship a **static adversarial probe over all 42 scenarios** with a
per-attack fool-rate. (2) Include a **human-oracle label** per attack and define
"fooled" = judge ≠ oracle (REV's bar). (3) Probe the **composed score** for the hedge
(RLE) — quantify the 0.55 shotgun. (4) Mark **verbatim-gold-echo informational** and
state the **eval-time exploitability caveat** loudly (SMR): gold text is hidden, so the
directly-reachable exploits are the ones needing only public symptom vocabulary
(hedge, single-token, negation, wrong-component, homoglyph). (5) Self-contained, no
core edits (DEV). Reachability via live RL = out of scope, logged as limitation.
