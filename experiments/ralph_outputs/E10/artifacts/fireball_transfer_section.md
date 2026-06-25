# 5.x Cross-Domain Transfer: FIREBALL → SRE

> **Section numbering is a placeholder** (`5.x`) to be fixed when this section lands in the
> draft; in the current outline it is §5.3 / contribution **C2**. This section is
> **self-contained**: it assumes the training procedure (§3.5), the 42-incident benchmark
> (§4), and the deterministic reward (§3.3) are defined elsewhere and references them; all
> other terms are defined here. **All result cells below are `PENDING`** — no transfer
> result is reported because the trained model and source corpus are not yet in the
> repository (see §5.x.5). This section is written as a **pre-registered protocol**.

**Abstract of the section.** We ask whether structured sequential-decision supervision from
an *unrelated* domain — the FIREBALL Dungeons & Dragons corpus, whose trajectories share the
`state_before → action → state_after` shape our SRE data already mirrors — transfers to
incident response, specifically to the *cascade* incidents where the loud alert points at a
victim and the naive fix worsens the outage. We state four hypotheses (H1–H4) with a null,
describe the methodology (FIREBALL SFT pretraining → GRPO on the opensre environment →
evaluation through the same pass@k harness and root-cause-aware reward used for every other
result in the paper), and lay out a seven-experiment design (E3–E9) with pre-registered
result tables. The headline metric is **trap-avoidance and correct-fix rate on cascades**,
not aggregate pass@1.

---

## 5.x.1 Hypothesis & motivation

**Why a Dungeons & Dragons corpus could possibly help an SRE agent.** FIREBALL is a corpus
of structured D&D play, where each step is a transition: a *state* (party, environment,
constraints), an *action* (a chosen move with declared intent), and a *resulting state*. Our
trajectory standard (`opensre-traj/SCHEMA.md`) mirrors this exactly — an SRE episode is a
sequence `system_state_before → tool/remediation → system_state_after`, extended from the
opensre diagnosis benchmark with the remediation our live bench actually performs. The
*conjecture* (explicitly labeled as such, tested by E6) is that a model pretrained to predict
**consequences of actions on a structured state** acquires a state-transition inductive bias
that is domain-agnostic: the surface tokens (goblins vs. CrashLoopBackOff) differ, but the
skill — "imagine the next state before committing to an action" — is shared, and it is
exactly the skill a cascade punishes you for lacking (scale the crash-looping control plane
and you herd its datastore).

We are deliberately conservative: the **load-bearing claim is narrow and empirical** (H1, on
cascades). The mechanism above is a conjecture, not a result.

| ID | Hypothesis | Null (falsification) | Primary metric |
|----|------------|----------------------|----------------|
| **H1** | FIREBALL pretraining improves performance on **cascade** incidents over an OpenSRE-only baseline. | Fireball-trained ≤ OpenSRE-trained on cascade correct-fix-rate, within the Wilson 95% CI → report **no / negative transfer**. | cascade correct-fix-rate + trap-avoidance-rate |
| **H2** | Transfer does **not hurt** simple incidents (no-harm guardrail). | Fireball-trained < OpenSRE-trained on simple-incident pass@1 beyond CI → report a **transfer tax**. | simple-incident pass@1 |
| **H3** | The **full** trajectory (state+action+state) carries the transfer, not state-only or action-only. | Ablated variants match full-trajectory transfer → the gain is not from state-transition structure. | cascade correct-fix-rate across ablations |
| **H4** | Transfer beats an **equal trajectory budget** of synthetic SRE augmentation — i.e. the gain is *transfer*, not merely *more data*. | Fireball-trained ≤ synthetic-augmented at matched budget → the effect is data volume, not cross-domain structure. | cascade correct-fix-rate at matched N |

**MVP (load-bearing) experiments: E3 (H1) and E4 (H2).** E5–E9 strengthen and probe the
mechanism but are not required for the core claim; they are labeled *strengthening / future*.

---

## 5.x.2 Methodology

**Pipeline.** (1) **FIREBALL SFT pretraining** on the D&D state-transition corpus
(`incidents.jsonl`, the source domain). (2) **GRPO** on the opensre SRE environment
(`opensre-traj/hud_env_v2.py`), with the deterministic root-cause-aware reward wired into the
grader and **group sizes chosen for within-group reward spread** (without spread, GRPO has no
gradient — see §3.5). (3) **Evaluation** of the resulting policy, *frozen*, through the same
machinery as every other result in the paper: the pass@k engine (`rex/eval_pass_at_k.py`) on
the 42-incident benchmark, graded by the deterministic reward (`rex/scoring.py`).

**The reward (the metric the section is graded on).** Identical to the rest of the paper, so
transfer is measured on the same scale:

```
score = 0.30·diagnosis_correct + 0.25·correct_fix + 0.45·resolved − 0.60·trap   (clamp 0..1)
```

**Operational definition of the headline metric.** *Trap-avoidance-rate* :=
`1 − (fraction of rollouts in which the −0.60 trap action fires)`, computed by the same
deterministic grader (`rex/scoring.py`). *Correct-fix-rate* := fraction of rollouts whose
emitted remediation matches the ground-truth causal fix. Both are reported **per incident
family** so that easy simple-incident wins cannot mask cascade behavior.

**Reconciling the frozen-LLM spine with this fine-tuned contribution (important).** The
paper's spine (contributions C1/C3) is deliberately *code-as-policy / auto-harness*: the
**deployed** policy is a frozen, swappable LLM wrapped by the REx Thompson-tree refinement
loop and a synthesized safety gate — reliability comes from evolving *code around* the model,
not from updating weights. This transfer study (C2) is a **separate, optional** question:
does cross-domain *training data* produce a better *base* policy — one you then freeze and
run through the exact same harness? Both can be true without contradiction, because **the
harness and the reward are the constant**; only the base checkpoint changes. We state this as
an owned design choice: C2 is the one place we fine-tune, and we evaluate its product under
the frozen-policy regime so its result is comparable to C1/C3. If the transfer model never
materializes (§5.x.5), the spine is unaffected and C2 degrades gracefully to a pre-registered
future experiment.

---

## 5.x.3 Experiment design (E3–E9)

These experiments are enumerated in the project's task ledger
(`experiments/NEXT_100_TASKS.md`, Category E). The benchmark, the three policies
(Fireball-trained / OpenSRE-trained / zero-shot), the pass@k engine, and the deterministic
reward are all in place; only the trained model and source corpus are pending (§5.x.5).

| ID | Question | Design | Primary metric | Control / comparison | Status |
|----|----------|--------|----------------|----------------------|--------|
| **E3** | Does transfer help cascades? *(H1, MVP)* | Fireball-trained vs OpenSRE-trained vs zero-shot on the **14 cascade** incidents; pass@1 by family. | cascade correct-fix + trap-avoidance | OpenSRE-trained and zero-shot baselines | pending (needs E1/E2) |
| **E4** | Does transfer *hurt* simple incidents? *(H2, MVP guardrail)* | Fireball-trained vs OpenSRE-trained on the **8 simple** incidents. | simple-incident pass@1 | OpenSRE-trained baseline | pending (needs E1/E2) |
| **E5** | Does it generalize to **novel** incidents? *(strengthening)* | Fireball transfer on **10 novel** incidents, **held out by failure-family** (no family overlap with training). | novel-incident pass@1 | OpenSRE-trained baseline | pending (needs E1/E2) |
| **E6** | *Which* part of the trajectory transfers? *(H3, mechanism)* | Ablate FIREBALL supervision: **full** vs **state-only** vs **action-only**. | cascade correct-fix-rate | full-trajectory variant | pending (needs E1/E2) |
| **E7** | Is D&D special, or do other game domains transfer too? *(frontier / future)* | Transfer from a **text-adventure** source domain, not only D&D. | cascade correct-fix-rate | FIREBALL (D&D) source | pending (needs source corpus) |
| **E8** | How much source data is needed? *(scaling)* | Vary FIREBALL trajectory budget: **1k / 10k / 50k**. | cascade correct-fix-rate vs N | within-experiment scaling | pending (needs E1/E2) |
| **E9** | Transfer, or just *more data*? *(H4, the key control)* | Fireball transfer vs **synthetic SRE augmentation at equal trajectory budget** (same N). | cascade correct-fix-rate at matched N | budget-matched synthetic augmentation | pending (needs E1/E2) |

---

## 5.x.4 Pre-registered results

> **Every data cell below is `PENDING`.** No number is reported until the model and corpus
> land. Reported integers elsewhere (14 cascades, 8 simple, 10 novel) are *benchmark sizes*,
> not results. We pre-register the tables so that, on unblock, results drop into labeled cells
> and the analysis (Wilson 95% CIs, McNemar paired tests across policies) is fixed in advance.

### T1 — E3: cascade pass@1 by family + trap-avoidance (headline)

| Incident family | Fireball-trained | OpenSRE-trained | Zero-shot |
|-----------------|------------------|-----------------|-----------|
| DNS / dependency-resolution | `PENDING` | `PENDING` | `PENDING` |
| Control-plane crash-loop | `PENDING` | `PENDING` | `PENDING` |
| Config-crash | `PENDING` | `PENDING` | `PENDING` |
| Upstream-dependency cascade | `PENDING` | `PENDING` | `PENDING` |
| Resource exhaustion | `PENDING` | `PENDING` | `PENDING` |
| **Correct-fix-rate (all cascades)** | `PENDING` | `PENDING` | `PENDING` |
| **Trap-avoidance-rate (headline)** | `PENDING` | `PENDING` | `PENDING` |

### T2 — E4 / E5: no-harm guardrail + generalization

| Incident set | Fireball-trained | OpenSRE-trained |
|--------------|------------------|-----------------|
| Simple incidents (E4, no-harm) | `PENDING` | `PENDING` |
| Novel incidents (E5, generalization) | `PENDING` | `PENDING` |

### T3 — E6 / E8 / E9: ablations & controls (cascade correct-fix-rate)

| Variant | Cascade correct-fix-rate |
|---------|--------------------------|
| FIREBALL full trajectory (E6) | `PENDING` |
| FIREBALL state-only (E6) | `PENDING` |
| FIREBALL action-only (E6) | `PENDING` |
| 1k trajectories (E8) | `PENDING` |
| 10k trajectories (E8) | `PENDING` |
| 50k trajectories (E8) | `PENDING` |
| Synthetic SRE augmentation, equal budget (E9) | `PENDING` |

**Falsification criterion (pre-registered).** If, for **H1**, the Fireball-trained policy
does **not** exceed the OpenSRE-trained policy on cascade correct-fix-rate beyond the
benchmark's Wilson 95% confidence interval, we report **no transfer** (or **negative
transfer** if strictly worse) — and C2 is reframed in the contributions list from a positive
result to a *measured null*. The hypothesis is allowed to lose.

---

## 5.x.5 Status & blockers

This section is **currently blocked on data and a model checkpoint**, not on the harness:

- **E2 — source corpus absent.** The FIREBALL D&D trajectory dataset (`incidents.jsonl`,
  referenced in `opensre-traj/README.md`) is not in the repository. FIREBALL presently exists
  in the project *only as a schema inspiration* (`opensre-traj/SCHEMA.md`,
  `opensre-traj/lib_opensre.py` mirror its `state_before → fix → state_after` shape). The
  data physically present is the OpenSRE corpus (`opensre-traj/out/trajectories.jsonl`) — the
  *target* domain, not the FIREBALL *source* domain.
- **E1 — trained model not pushed.** The Fireball-trained checkpoint (Wenji's GRPO branch /
  the fireball-trained Qwen slug) has not been pushed and is not on HUD. Consistent with
  `experiments/CLAIMS_EVIDENCE.md` ("GRPO run not yet pushed to repo") and
  `experiments/results/P7_fireball_status.md`.

**Everything else is ready.** The 42-incident benchmark, the pass@k engine
(`rex/eval_pass_at_k.py`), the deterministic root-cause-aware reward (`rex/scoring.py`), the
GRPO env (`opensre-traj/hud_env_v2.py`), and the three-policy comparison protocol all exist.

**Run recipe once unblocked.** Set each of the three policies (Fireball-trained,
OpenSRE-trained, zero-shot) as the agent and run the cascade benchmark through the existing
pass@k engine, comparing pass@1 and trap-avoidance by incident family — e.g. run
`rex/eval_pass_at_k.py` with each model slug over the 14 cascade incidents, then populate
T1–T3. The deterministic reward makes the comparison reproducible without an LLM judge.

**Fallback if E1/E2 never land before submission.** The section ships as the
pre-registered protocol above and C2 moves, in the contributions list, from a claimed result
to a stated future experiment. The paper's spine (C1 harness synthesis, C3 SME-feedback RLVR)
does not depend on C2 and is unaffected.

---

## 5.x.6 Threats to validity

- **Confounding transfer with data volume.** Addressed by E9 (budget-matched synthetic
  augmentation). If E9 is unrun, H1 alone cannot distinguish "cross-domain structure helped"
  from "more trajectories helped."
- **Single source domain.** Positive transfer from FIREBALL alone does not establish that
  *games in general* transfer; E7 (text-adventure source) is the stated generalization test
  and is currently a frontier item, not a result.
- **Frozen-vs-fine-tuned framing tension.** The deployed system is a frozen policy + harness;
  C2 fine-tunes the base checkpoint. We evaluate the fine-tuned product under the frozen
  regime through the same reward so results are comparable (§5.x.2), but a reader should note
  that C2 is the one contribution that updates weights.
- **Benchmark provenance.** Cascade incidents are reconstructed from real public post-mortems
  (e.g. AWS DynamoDB DNS, Cloudflare WAF, CrowdStrike CF291) and synthetic single-leaf
  incidents; if a pretrained base has seen those post-mortems in text form, apparent transfer
  could be contamination rather than structural transfer. The held-out-by-family novel set
  (E5) partially controls for this; full decontamination is a stated limitation.
- **Mechanism is conjecture.** The state-transition-inductive-bias story is tested only
  indirectly by E6; we do not claim a representation-level mechanism without that ablation.
