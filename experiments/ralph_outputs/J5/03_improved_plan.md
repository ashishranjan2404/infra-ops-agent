# 03 — Improved Plan (post-grill)

## What changed vs 01
1. **Honest mechanism labelling** (RLE, AAAI accepted). The case study explicitly
   names: frozen LLM *proposer* (not a trained policy), `gpt-5.5` via the HUD
   gateway (Anthropic credits exhausted → the haiku default 400s), deterministic
   keyword judge (`REX_JUDGE_MODE=deterministic`), Tier-A sim, scenario `seed:1076`.
2. **Two-part narrative** (SMR vs PSRE synthesis). The case study separates:
   - *Agent contribution*: correct **upstream** diagnosis at **iter 0**, before any
     feedback — the hard part of this cascade.
   - *Harness contribution*: the `is_safe` trap-gate that blocks scaling the loud
     victim (`edge-proxy`).
3. **Counterfactual trap branch added** (DOL accepted) **and flagged as
   by-construction** (AAAI accepted). I run `scale_deployment(edge-proxy)` through
   the sim and show it is *blocked* (forbidden `saturation` category) and does
   **not** resolve — and I say plainly this is a designed property of the reward.
4. **Verbatim reasoning + feedback strings** included (DOL accepted).
5. **Scope statement** added (AAAI accepted): N=1 illustrative case study, not a
   metric. Aggregate numbers live in other tasks; this one shows the mechanism.

## Critiques accepted
- AAAI "N=1, label by-construction, add repro metadata" → fully accepted.
- RLE "it's a frozen proposer loop, make the env legible" → accepted; spec lists
  action space + gate.
- DOL "show the counterfactual + quote reasoning" → accepted.
- SMR/PSRE both-halves → accepted as the narrative spine.

## Critiques rejected (and why)
- SMR's implicit ask to *prove* the feedback (not re-sampling luck) caused iter-1.
  **Rejected** as out of scope for a case study: isolating feedback-vs-resample
  causally needs an ablation (N≫1, fixed seeds, feedback-off control) — that's a
  different task. I instead *report* the observed iter-0→iter-1 transition
  transparently and flag the causal claim as unproven.
- PSRE's "credit assignment is irrelevant, only the gate matters." **Rejected**:
  reduces the agent to the harness. The iter-0 correct diagnosis (which the gate
  did not supply) is exactly the agent's measurable competence and must be shown.

## Unchanged
Scenario, the runnable artifact, the deterministic fallback, the no-core-edit rule.
