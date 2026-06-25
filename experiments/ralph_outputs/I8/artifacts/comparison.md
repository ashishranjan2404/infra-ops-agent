# Code-as-Policy vs RLHF vs Constitutional AI

*A rigorous comparison, grounded in the SRE-Degrees auto-harness.*

## TL;DR — the unifying frame

All three paradigms are mechanisms for injecting **human normative knowledge** into the behavior of
a large language model. They differ in **where that knowledge physically lives** and **how it gets
enforced**:

| Paradigm | Knowledge substrate | Enforcement mechanism |
|---|---|---|
| **RLHF** | model **weights** (via a learned reward model) | gradient descent (PPO) against a learned reward + KL leash |
| **Constitutional AI** | model **weights + a written constitution** | self-revision (SL) then RLAIF (PPO against an AI preference model) |
| **Code-as-policy** (this repo) | **explicit code** (reward fn, safety gate, registry) around a *frozen* model | verifier-guided inference-time search + a rejection gate (no weight change) |

The axes below are **not a scorecard.** Each paradigm is strongest in its native domain. The single
most important caveat: **code-as-policy only works where you can write a verifier.** RLHF and CAI
exist precisely for the regime where you *cannot* (tone, helpfulness, harmlessness, honesty).

---

## 1. Precise definitions

**RLHF (Reinforcement Learning from Human Feedback).** Humans rank model outputs pairwise; a
**reward model** is trained to predict those preferences; the policy is then optimized by a
policy-gradient method (typically **PPO**) to maximize that learned reward, with a **KL-divergence
penalty to a reference (SFT) policy** to prevent the policy from drifting into reward-hacked,
off-distribution text. Lineage: Christiano et al. 2017 (deep RL from human preferences),
InstructGPT / Ouyang et al. 2022. Net effect: human taste is distilled into **weights** through a
learned, imperfect reward proxy.

**Constitutional AI (CAI / RLAIF).** Two stages (Bai et al. 2022, "Constitutional AI: Harmlessness
from AI Feedback", Anthropic):
1. **Supervised stage (SL-CAI):** the model is prompted to **critique and revise its own responses**
   against a set of written **principles (the "constitution")**, and is fine-tuned on the revised
   responses.
2. **RL stage (RLAIF):** a **preference model is trained on AI-generated comparisons** (the AI,
   guided by the constitution, picks the better of two responses), then PPO optimizes against it.
   CAI replaces the *human* preference label with an *AI* label conditioned on principles. Knowledge
   lives in **weights**, but a distinguished, human-readable slice of it lives in the **constitution
   text** itself.

**Code-as-policy (this repo's auto-harness).** The LLM is a **frozen, swappable policy**
(`agent/llm.py`, `agent/models.py`): the same code runs Claude Opus/Haiku, GPT-5.x, Gemini-3.x,
DeepSeek-v4 behind one interface, with **no weight updates to any of them**. Reliability comes from
**code that wraps the model**:
- a **deterministic, root-cause-aware reward** —
  `score = 0.30·diagnosis + 0.25·correct_fix + 0.45·resolved − 0.60·trap` (`rex/scoring.py`);
- a **rejection/safety gate** + trust-tier tool registry (`rex/harness.py`, `tools_registry.json`)
  that blocks unsafe remediations before they execute;
- **verifier-guided inference-time search** — Thompson sampling over candidate refinements
  (`rex/tree.py::thompson_search`, driven by `rex/loop.py`), and an escalation handoff when no safe
  fix exists;
- a **code world model / simulator** that makes cascades *emergent*, not scripted (`sim/engine.py`,
  `scenarios/cidg/generated/*.yaml`).

Mechanistically this is **verifier-guided inference-time search over a frozen policy plus a
rejection safety gate** — *not* policy-gradient. (Colloquially people call any closed improvement
loop "RL"; for rigor we keep the precise label.) Lineage: code-as-policy / auto-harness /
code-world-model.

---

## 2. The five axes

### Axis 1 — Where knowledge lives
- **RLHF:** in **weights**, as an opaque distillation of a *learned* reward model. Not directly
  inspectable; you see behavior, not the rule.
- **CAI:** in **weights**, but a privileged, **human-readable** part of the specification — the
  **constitution** — is explicit text. This is CAI's signature advantage: the *intent* is auditable
  even if its weight imprint is not.
- **Code-as-policy:** in **explicit, version-controlled code** — `rex/scoring.py`'s reward weights,
  the safety gate, the tool registry. The norm *is* the artifact; nothing is latent in weights.

### Axis 2 — Verifiability
- **RLHF / CAI:** the reward is a **learned approximation of human (or AI) preference**. There is no
  oracle; the reward model can be — and is — **gamed** (sycophancy, verbosity, reward hacking). The
  KL leash and AI-feedback help but do not make the signal *ground-truth*.
- **Code-as-policy:** in this domain the reward is **ground-truth verifiable** — a fix counts only
  if the SLO metric **crosses back under threshold** AND the **diagnosis matches the gold mechanism**
  AND the **trap was not tripped** (`rex/scoring.py`). `resolved` alone is capped at 0.45, so a model
  that restarts/scales until the metric recovers but misdiagnoses scores 0.0 — explicit
  anti-reward-hacking.
- **Crucial honest caveat:** this verifiability is **conferred by the task, not by the method.**
  Incident response *has* an oracle (SLO recovery). Open-ended helpfulness/harmlessness — RLHF/CAI's
  home turf — has none. Do not generalize the oracle.

### Axis 3 — Sample efficiency (amortized capex vs per-call opex)
- **RLHF:** large **upfront** cost — on the order of tens of thousands of human pairwise comparisons
  (varies widely by setup) **+ reward-model training + a PPO run** — then **cheap at inference**
  (one forward pass). Capex-heavy, opex-light.
- **CAI:** removes **most human preference labels** (the AI generates them) — a real efficiency win
  on the most expensive input — but still pays for **two training stages**. Capex-medium,
  opex-light.
- **Code-as-policy:** **zero** preference labels, **zero** training. Cost is paid **per incident at
  inference**: the REx loop issues **multiple model calls** (propose → run → score → refine). Near-
  zero capex, **opex-heavy.** The comparable quantity is *marginal cost to improve behavior on a new
  task*: RLHF/CAI amortize one training run over all future queries; code-as-policy re-pays search
  cost every time.

### Axis 4 — Safety guarantees
- **RLHF / CAI:** safety is **statistical and post-hoc** — the model is *less likely* to misbehave,
  but there is **no hard guarantee**; jailbreaks and edge cases persist because the constraint lives
  in soft weights.
- **Code-as-policy:** safety can be a **hard, pre-execution gate.** The safety check / trust-tier
  registry **rejects an unsafe remediation before it runs** (`rex/harness.py`, autonomous/approval/
  blocked tiers), and when **no safe fix exists the system escalates to a human** rather than
  flailing — in the repo's curriculum the unsolvable incident (`singleton_node_notready`) is
  *escalated*, capping the achievable score at the "correct-escalation" ceiling instead of inviting
  a dangerous guess. This is a guarantee about *actions taken*, not about *text generated*.

### Axis 5 — Interpretability
- **RLHF:** **low** — the operative norm is latent in weights via a learned reward; you debug by
  probing behavior.
- **CAI:** **mixed** — the constitution is the **most legible statement of intent** of the three
  (plain-English principles), yet its *imprint on weights* is as opaque as RLHF's. Legible
  specification, opaque mechanism.
- **Code-as-policy:** **high** — the norm is **`git`-diffable, reviewable, and reversible.** You can
  read the exact reward weights, the safety predicate, and the tool tiers, change one, and roll it
  back. Interpretability is here **coupled to reversibility**: weight-baked knowledge cannot be
  hot-patched; code knowledge can.

---

## 3. Summary matrix

| Axis | Code-as-policy (this repo) | RLHF | Constitutional AI |
|---|---|---|---|
| **Knowledge location** | explicit version-controlled code (reward fn, safety gate, registry) | model weights (learned reward proxy) | weights + human-readable constitution |
| **Verifiability** | ground-truth (SLO recovery + gold diagnosis + trap), *task-conferred* | learned, gameable preference proxy | learned AI-preference proxy + principles |
| **Sample efficiency** | 0 labels, 0 training; opex-heavy (many inference calls/incident) | tens of thousands of human comparisons + RM + PPO; opex-light | few/no human labels (AI labels) + 2 train stages; opex-light |
| **Safety guarantees** | hard pre-execution gate + escalate-when-no-safe-fix | statistical / post-hoc, no hard guarantee | statistical / post-hoc, no hard guarantee |
| **Interpretability** | high — git-diffable, reversible norm | low — latent in weights | mixed — legible constitution, opaque imprint |

*Reminder: this is not a scorecard. Each column is best in its native domain.*

---

## 4. Where code-as-policy LOSES (honest limits)

1. **No verifier → no method.** Code-as-policy is inapplicable wherever you cannot write an oracle.
   "Was this answer kind / honest / non-toxic?" has no SLO. RLHF/CAI own that regime.
2. **It inherits the frozen model's ceiling.** Search + a verifier can only reach what the
   underlying model can produce when steered; it cannot install *new* capabilities or values into
   weights. In this repo every model + REx converges to the same solvable-set ceiling
   (~0.86 on the easy tier; see `ARCHITECTURE.md` / `rex/frontier.py`) — REx **compresses** the
   capability spread and **lifts weak models**, but does not exceed what model+verifier jointly
   reach.
3. **Opex, every time.** RLHF/CAI pay once and are cheap forever; code-as-policy re-pays inference
   search on each query. At very high query volume the amortized economics favor weight-baked
   methods.
4. **Verifier bugs become policy bugs.** If the reward code is wrong, the agent confidently optimizes
   the wrong thing — the failure is now in *your* code rather than in opaque weights. (Mitigant: it's
   at least *visible* and fixable — the interpretability axis cuts the other way here.)

---

## 5. Synthesis — complementary, not rivals

These paradigms occupy different layers:
- **RLHF** instills broad, fuzzy preference where no oracle exists.
- **CAI** makes that instillation **cheaper and its intent legible** by replacing human labels with
  principle-guided AI labels.
- **Code-as-policy** takes a model already shaped by RLHF/CAI and, **in verifiable domains**, wraps
  it in explicit, auditable, reversible code that gives **ground-truth reward and hard safety gates
  without touching weights.**

A production SRE agent ideally uses **all three**: an RLHF/CAI-aligned frozen model as the policy,
and a code-as-policy harness as the verifiable, hot-patchable safety-and-quality layer around it —
which is exactly the stack this repository builds.

---

### References / grounding
- Christiano et al. 2017, *Deep RL from Human Preferences*; Ouyang et al. 2022, *InstructGPT* (RLHF).
- Bai et al. 2022, *Constitutional AI: Harmlessness from AI Feedback*, Anthropic (CAI/RLAIF).
- This repo (code-as-policy): `agent/llm.py`, `agent/models.py`, `rex/harness.py`, `rex/loop.py`,
  `rex/tree.py` (`thompson_search`), `rex/scoring.py` (the weighted reward), `sim/engine.py`,
  `scenarios/cidg/generated/*.yaml`, and the measured results in `ARCHITECTURE.md`.
