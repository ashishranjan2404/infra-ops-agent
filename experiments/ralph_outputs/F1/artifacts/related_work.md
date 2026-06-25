## 2. Related Work

Our methodology sits at the intersection of four threads: (i) benchmarks and
harnesses for autonomous SRE agents, (ii) treating a policy as searchable *code* /
test-harness rather than weights, (iii) inference-time refinement search with a
verifier in the loop, and (iv) reinforcement learning from *verifiable* rewards and
from human/expert feedback. We position each against the three claims of this paper —
a synthesized safety harness (C1), cross-domain transfer (C2), and SME-feedback RLVR
(C3) — and are explicit about what we borrow versus what is new.

### 2.1 SRE agent benchmarks and harnesses

**SREGym** [Surana et al., 2026; arXiv:2605.07161] is the closest contemporary work
on the *evaluation* side. It is a 90-problem benchmark over a live Kubernetes
substrate with a pass@1 leaderboard (Claude Code currently tops it, roughly 40–60%
end-to-end success depending on category). Its problems are reconstructed from real
postmortems — Cloudflare WAF, conntrack/IP exhaustion, GKE IP exhaustion, Kafka
poison-pill — several of which also appear in our held-out *novel* family. The crucial
differences are scope and substrate. SREGym is a *benchmark*: it scores agents
end-to-end but exposes no cascade taxonomy and no per-incident **trap-action** labels,
and it requires a live cluster to iterate. We instead contribute a *training
methodology* over a lightweight Tier-A transition sim (`sim/engine.py::propagate`), in
which cascades, misleading loudness, and worsening-naive-fixes are *emergent* from one
transition kernel rather than hand-scripted, and in which `is_resolved` is
ground-truth (`root_cleared AND SLO recovered`) rather than a heuristic. This lets us
iterate the refinement loop thousands of times with no cluster and grade with a
*deterministic* reward (§2.4). We treat trap-action avoidance as a first-class metric,
which SREGym does not measure directly.

**AIOpsLab** [Chen et al., 2024/2025] and **ITBench** [IBM Research, 2025] are the
prior academic harnesses that SREGym builds on. AIOpsLab provides an
agent–cloud-operations interface with fault injection (detection, localization, root-
cause analysis, mitigation) over microservice testbeds; ITBench packages a broader set
of IT-automation scenarios (SRE, FinOps, CISO) with reproducible environments. Both
establish the "inject a fault, let an agent operate the cluster, grade the outcome"
paradigm that SREGym and we inherit. Neither searches for its safety rules, and neither
isolates an SME-feedback training signal — they are evaluation environments, not
training loops.

**Commercial AI-SRE systems** — Komodor's *Klaudia*, Datadog's *Bits AI SRE*, and
Resolve.ai — target the same MTTR bottleneck in production. They are closed,
telemetry-coupled, and publish no public pass@k, no cascade taxonomy, and no harness-
synthesis or SME-feedback procedure. We cite them to delimit the problem (root-cause
localization on cascades dominates MTTR) but cannot compare numerically.

### 2.2 Code-as-policy and Code World Models

The agent's *policy* in our system is a structured plan `{root_cause, ordered
tool-calls}`, and its *safety layer* (`is_safe`) is interpreted **data** (rules over a
fixed feature set), not free-form executable LLM output — we never `exec` model output;
trusted code interprets the rules. This design inherits the **code-as-policy** line of
work [Liang et al., *Code as Policies*, 2023], which showed that an LLM emitting
*program* actions (composable, inspectable, verifiable) generalizes and debugs better
than one emitting opaque actions.

Most directly, Meta's **Code World Models (CWM)** [Meta FAIR CodeGen Team, 2025] argues
that a model trained to predict the *effects of code execution* — observation/action/
next-state traces and Python interpreter dynamics — learns a usable world model for
agentic reasoning. Our simulator is exactly such an explicit world model for the SRE
domain: a typed topology with a single `propagate` transition kernel and a
root-cause-aware `is_resolved`, against which a candidate plan is *executed* and graded
by its effect on the SLO. Where CWM *learns* execution dynamics inside the network, we
keep the world model external, deterministic, and cheap so it can serve as a
ground-truth verifier in the refinement loop (§2.3) and as the GRPO grader (§2.4). The
shared thesis is that grounding an agent in *executable state transitions* — rather than
in textual plausibility — is what makes its reasoning checkable. This same
`state_before → action → state_after` schema motivates our transfer hypothesis (§2.5).

### 2.3 AutoHarness: synthesizing the verifier/harness

Our safety harness is not hand-authored from intuition: it is a **searched artifact**.
`rex/harness_synth.py` runs Thompson-tree search (`rex/tree.py::thompson_search`) over
candidate rule-sets, with a small frozen model (Haiku) acting *only* as the mutation
operator that proposes edited rule-sets, and classification accuracy on *training*
incident labels as the reward. We then measure **held-out** verifier accuracy: synthesize
on a 7-incident train split, gate unsafe actions on a disjoint 3-incident held-out split
the harness never saw. This synthesize-the-harness framing follows the **AutoHarness**
line of work on *automatically generating test harnesses / verifiers* rather than
hand-writing them. The conceptual debt is the same as in automated unit-test and
specification synthesis [e.g., property-based and search-based test generation, and
LLM-as-test-author systems such as TestGen-LLM, Alshahwan et al., 2024]: a verifier you
*search for* against labelled outcomes can be more complete and less brittle than one a
human enumerates. Our specialization is (a) the search operates over *interpretable*
rule data consumed by trusted code, never over executable model output; (b) the reward
is held-out classification accuracy, so a same-set "learned lookup" cannot win; and (c)
the hand-written `is_safe` is preserved intact as the human upper bound, letting us
report the gap directly (seed 66.7% → synthesized-v2 89.7% → hand-written 94.9%
held-out accuracy, with a 14→3 rule compression that *reduces* false-allows).

### 2.4 Inference-time refinement search: REx and the verifier loop

The training-signal claim (C3) rests on a refinement *search*, not single-shot
sampling. **REx** [*Refinement with Exploration / refinement-tree search*, Tang et al.,
2024] reframes iterative LLM self-improvement as a bandit problem: keep every candidate
solution as a node, maintain a posterior over each node's quality, and Thompson-sample
which node to *expand* (refine) next, rather than always refining the latest attempt.
We implement exactly this in `rex/tree.py`: each candidate carries a `Beta(α, β)`
posterior seeded by its own score; each round samples `θ ~ Beta` per node, expands the
argmax, and tightens the parent by its child's score — deterministic under `seed`. This
is a strict generalization of the linear refine loop (`rex/loop.py`), which always
refines the most recent candidate.

The other half of the loop is the **verifier**. Like reflection/self-refinement methods
(Self-Refine [Madaan et al., 2023], Reflexion [Shinn et al., 2023]) and verifier-guided
search (e.g., process/outcome reward models and tree-of-thoughts [Yao et al., 2023]), an
external signal drives the next attempt. Our distinction is the *kind* of signal and a
controlled ablation of it. The **SME (subject-matter-expert) feedback** condition reveals
the gold mechanism and the resolving tool when the agent's diagnosis is wrong; the
**no-oracle / realistic** control reveals only "still breaching / action blocked" — the
information a real on-call engineer gets from telemetry alone. This lets us isolate the
*value of the oracle*: REx with SME feedback yields a large, McNemar-significant pass@1
lift on cascades, while REx-no-oracle collapses to roughly zero-shot on the novel
family — an honest generalization gap that pure self-refinement papers do not surface,
because they rarely separate "search helped" from "an oracle leaked the answer."

### 2.5 Cross-domain transfer: FIREBALL

The transfer claim (C2) draws on **FIREBALL** [Zhu et al., 2023; ACL], a corpus of
~25k Dungeons & Dragons play sessions from Discord with structured *Avrae* command
state: each turn is logged as `state_before → action → state_after`. We hypothesize
that this explicit state-transition structure — not the fantasy content — is what
transfers to SRE incident handling, where an agent must likewise reason `current_state
→ remediation_action → resulting_state`. To our knowledge no prior SRE agent is trained
on out-of-domain trajectory data; every system in §2.1 trains (if at all) on SRE-
specific traces. If FIREBALL pretraining lifts cascade pass@1 over SRE-only training,
it suggests the field does not require expensive SRE-specific demonstration data to
learn the *transition-modeling* skill. We treat this as a hypothesis under test, not a
settled result (status pending the GRPO transfer branch, §7).

### 2.6 Verifiable rewards (RLVR / GRPO) and learning from feedback

The training distillation (C3, RLVR portion) uses **GRPO** [Shao et al.,
*DeepSeekMath*, 2024], the group-relative policy-optimization algorithm popularized by
DeepSeek-R1 [DeepSeek-AI, 2025], with the deterministic simulator reward wired into the
grader and groups sized for within-group reward spread (σ, the unit GRPO actually
optimizes). This places us in the **RLVR** (RL from Verifiable Rewards) paradigm
[Lambert et al., *Tülu 3*, 2024; and the math/code-RL line], where the reward is a
checkable program output rather than a learned or LLM-judge score.

Our specific contribution to this thread is a **deterministic verifiable reward** for a
*diagnostic* task. The score is graded —
`0.30·diagnosis + 0.25·correct-fix + 0.45·resolved − 0.60·trap` (`rex/scoring.py`) —
and, critically, the 30% *diagnosis* term is a **deterministic keyword-set judge**: a
gold-mechanism-vs-red-herring discriminative-token vote with light stemming and a small
synonym map, replacing the noisy Haiku LLM-judge used in earlier iterations. This is a
direct response to the well-documented unreliability of **LLM-as-a-judge** rewards
[Zheng et al., *MT-Bench / LLM-as-a-Judge*, 2023], which inject per-step sampling noise
into training and are not reproducible. Going deterministic removes a noise source from
the GRPO signal entirely and makes every reward credit-free and replayable; the
trade-off is paraphrase recall, which we mitigate with discriminative-token voting and a
`hybrid` mode that defers only borderline-overlap cases to an LLM. We thus extend RLVR
from settings with a natural checker (math answer, unit test) to *root-cause diagnosis*,
where the "ground truth" is a mechanism description rather than a number.

Finally, the SME-feedback loop is a lightweight cousin of **RLHF / RLAIF and
Constitutional AI** [Bai et al., *Constitutional AI*, 2022]. Constitutional AI replaces
human preference labels with a fixed set of *principles* the model critiques and revises
against; our harness plays an analogous role — a set of explicit, inspectable *safety
rules* that gate (and, via blocked-action feedback, shape) the agent's behavior. The
differences are that our "constitution" is (a) *synthesized by search* rather than
hand-written (§2.3), (b) enforced by trusted code as a hard gate rather than absorbed
into a preference model, and (c) grounded by a ground-truth simulator rather than by a
second LLM's judgment, so the corrective signal is verifiable rather than self-
generated.

### 2.7 Statistical methodology

We report **pass@k** with the unbiased estimator and Wilson 95% intervals [Wilson,
1927], following its standard use for code/agent evaluation [Chen et al., *Evaluating
LLMs Trained on Code* / HumanEval, 2021], and we compare conditions on identical
(incident, seed) pairs with **McNemar's exact paired test** [McNemar, 1947] rather than
comparing mean rewards. This paired, interval-reported protocol is what lets us claim
the REx(SME)-vs-control gaps are real rather than noise — a level of statistical rigor
the commercial systems (§2.1) do not provide and that benchmark leaderboards (§2.1)
typically omit.

---

#### Summary of positioning

| Thread | Representative work | What we borrow | What is new here |
|---|---|---|---|
| SRE benchmark | SREGym, AIOpsLab, ITBench | postmortem-grounded incidents, pass@1 | trap-action labels, cascade taxonomy, lightweight sim, a *training* loop |
| Code-as-policy / world model | Code as Policies; Meta CWM | executable state-transition grounding | external deterministic world model used as verifier + GRPO grader |
| Harness synthesis | AutoHarness; TestGen-LLM | *search* the verifier, don't hand-write it | rules-as-data over fixed features; held-out verifier accuracy; human upper-bound kept |
| Refinement search | REx; Reflexion; Self-Refine; ToT | Thompson-tree over candidates + verifier feedback | SME-vs-no-oracle ablation isolating oracle value |
| Transfer | FIREBALL | `state_before→action→state_after` schema | D&D→SRE cross-domain transfer (untested elsewhere) |
| RLVR / feedback | GRPO/DeepSeek-R1; Tülu-3 RLVR; Constitutional AI; LLM-as-judge | verifiable-reward RL; principle-based shaping | *deterministic* diagnosis reward (no LLM judge); searched constitution as hard gate |
