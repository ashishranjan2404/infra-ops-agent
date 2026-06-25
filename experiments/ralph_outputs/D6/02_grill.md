# D6 — 02 Grill (5 personas x 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial takes
- **SMR:** DPO from existing reward-ranked trajectories is sound — it's essentially
  RLHF-from-AI-feedback where the "human" is the deterministic SRE judge. The pairs
  are cheap and abundant. Watch the reference policy: DPO needs a frozen ref, and the
  trajectories came from *different* models, not the policy you're training, so this
  is off-policy preference data. That's fine for DPO but worth stating.
- **PSRE:** I care that "chosen" actually reflects what an on-call would accept. A
  reward of 0.68 vs 0.22 is a real gap; a correct root_cause + safe remediation beats
  a confidently-wrong one. The framing as "override data" is legitimate: escalate/
  override is exactly accepting one diagnosis over another. Good.
- **AAAI:** Novelty is modest — DPO-from-reward is known. The contribution here is the
  *override-loop* framing and that the same deterministic judge both generates and
  evaluates. Reviewers will ask: is the prompt faithfully reconstructed? Is there
  train/eval leakage (same scenarios)? Address both.
- **RLE:** Mirror train_rft.py so it's obviously the DPO sibling of the GRPO run.
  Need beta, ref-free flag, loss_type. Don't actually try to train a closed model —
  same constraint as GRPO: only open forks are trainable.
- **DOL:** Make it runnable without a GPU in CI. A --dry-run that validates data and a
  real path that fails loudly with an actionable blocker. No silent fake numbers.

## Round 2 — genuine disagreement (react by name)
- **AAAI vs SMR:** SMR called the pairs "abundant", but I disagree on quality. Many
  same-scenario pairs differ by reward yet may have *near-identical* answer text from
  the same model family — those are degenerate pairs that teach nothing and can even
  destabilize DPO (chosen≈rejected). You must dedup identical text and set a real
  margin floor, not just margin>0.
- **SMR concedes partially:** Fair — I'll require dedup + min_margin (~0.1). But I
  reject the implication that off-policy pairs are useless; DPO tolerates them.
- **PSRE vs RLE:** RLE wants to mirror GRPO config wholesale. I push back — DPO's
  learning rate must be *much* lower (5e-7-ish) than typical SFT/GRPO, or you'll
  blow up the policy. Don't copy GRPO hyperparams blindly.
- **RLE responds:** Agreed, I'll set lr=5e-7, beta=0.1, cosine — DPO-specific, not
  copied from the RFT script.
- **DOL vs AAAI:** AAAI worries about leakage; I counter that for *this deliverable*
  (constructor + scaffold) leakage is an eval-protocol concern, not a pair-construction
  bug. We should note it but not block on it — eval uses held-out scenarios via the
  existing eval_pass_at_k.py.
- **AAAI holds ground:** Accept the scoping, but the config MUST name the held-out
  eval path so a reviewer sees we thought about it.

## Round 3 — synthesis
Consensus: (1) construct pairs per-scenario only (no cross-scenario), (2) enforce
min_margin + dedup identical text + skip empty answers, (3) DPO-specific hyperparams
(low lr, beta, frozen ref), (4) runnable dry-run + honest backend blocker, (5) document
off-policy nature and the held-out eval protocol to preempt leakage critique.
Unresolved-but-noted: prompt reconstruction from templated specs is approximate;
flagged as a known limitation, not a blocker.
