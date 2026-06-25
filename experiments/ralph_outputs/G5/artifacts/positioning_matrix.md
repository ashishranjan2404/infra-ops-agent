# Positioning Matrix — SRE-Degrees (us) vs SREGym vs Komodor vs Datadog Bits AI

**Snapshot:** 2026-06. Capabilities of commercial products move fast; every competitor claim is
date-stamped in `sources.json` and tagged below.

**Category disclaimer (read first).** These four are *not the same kind of thing*, and this matrix
compares **posture**, not a single overall ranking:
- **SRE-Degrees (us)** — a research **RL environment + trajectory generator**. A *frozen,
  swappable* LLM is the policy; reliability comes from the environment + a root-cause-aware
  reward. We ship *graded data and a harness*, not a product. [S1]
- **SREGym** — an academic **live benchmark** for AI SRE agents. Evaluation substrate, not a
  product. [S2]
- **Komodor** — a **deployed commercial SaaS** ("Klaudia" agents) that installs into your
  Kubernetes account and can auto-remediate, with or without a human in the loop. [S5][S6]
- **Datadog Bits AI SRE** — a **deployed commercial agent** inside Datadog that investigates
  alerts against your live telemetry. [S8][S9]

No public, shared benchmark exists across all four. Where we have not run a head-to-head, the
matrix says so. We are honest about where we *lose* (deployment, eval scale).

## The matrix

| Dimension | SRE-Degrees (us) | SREGym | Komodor | Datadog Bits AI |
|---|---|---|---|---|
| **Open benchmark** | Open: in-repo specs + sim + 33 generated CIDG scenarios + reconstructed real outages, reproducible offline `[S1]` | Open-source live benchmark, 90 SRE problems, fault/noise injectors over real stacks `[S2][S3]` | Closed product; no public benchmark; field metrics only `[S5][S6]` | Closed; internal benchmark on proprietary customer incidents, not public `[S10][S11]` |
| **Trap-action safety** | Explicit: reward subtracts **−0.60** for the harmful "trap" action (e.g. scaling a crash-looping control plane → herds its datastore); modeled in sim + GKE test cluster, not live prod `[S1]` | Models metastable & correlated failures where naive fixes fail, but reports diagnosis/mitigation success — no published per-action trap *penalty* `[S2]` | Acts on live prod; "self-healing with or without human in the loop"; safety is human-in-the-loop gating, no public trap-penalty metric `[S6][S7]` | Human-in-the-loop triage/remediation from chat; safety via human approval, not a published trap-penalty `[S8][S9]` |
| **Training method** | Frozen policy → emits **reward-shaped trajectories with within-group spread** (0.0/0.15/1.0) for downstream RL; no fine-tuning of the policy itself `[S1]` | Evaluation-only benchmark; positioned as a "live training ground" but provides the environment, not a training algorithm `[S2][S4]` | Proprietary multi-agent product "trained on thousands of production environments"; method not disclosed `[S5][S6]` | Proprietary; labels real incidents to build internal eval set; training method not disclosed `[S10][S11]` |
| **Deployment posture** | **Not deployed** — research harness + a GKE *test* cluster; no customers, no prod install `[S1]` | Benchmark you self-host to evaluate agents; not a prod deployment `[S2][S3]` | **Deployed in enterprise prod** (Cisco, Dell, BlackRock cited); installs into K8s, auto-remediates `[S5]` | **Deployed**; tested across 2,000+ customer environments, tens of thousands of investigations `[S8][S9]` |
| **Evaluation rigor** | Root-cause-aware reward (grades *mechanism* + correct fix + trap, not "did it come back up"); but small n (5 models × 5 incidents), LLM-judge, **not head-to-head** vs others `[S1]` | Larger external benchmark: 90 problems, multiple agent/model pairs, reported diagnosis 38.9–72.6%, mitigation 57.3–78.5% `[S2]` | Vendor-reported "95% accuracy", "40% fewer tickets" — no public methodology, not independently verified `[S5]` | Vendor-reported "twice as fast / more accurate" on an *internal, proprietary* benchmark; no independent RCA benchmark exists `[S10][S11]` |

## Per-dimension notes

**Open benchmark.** We and SREGym are the only two that are publicly reproducible; this is a *tie*
on openness, with SREGym ahead on scale (90 live problems vs our 33 generated + handful of
reconstructed cascades) and us ahead on the *reward* being open, not just the faults `[S1][S2][S3]`.
Komodor and Datadog publish no reproducible benchmark `[S5][S10]`.

**Trap-action safety.** Our sharpest honest edge: a *quantified* penalty on the specific harmful
action, baked into the reward `[S1]`. Caveat (we lose nuance here): this is *modeled* in a
deterministic sim and a controlled GKE cluster — it is not the messy live-prod risk Komodor and
Datadog actually take. They handle real prod risk via human-in-the-loop gating, which is a
different (and in production, more demanding) safety model `[S6][S7][S8]`.

**Training method.** The one axis where we are uniquely first publicly: a *frozen* policy producing
reward-shaped trajectories with genuine within-group spread — training *data*, not a fine-tune
and not an orchestration product `[S1]`. SREGym is eval-only `[S2]`; the two vendors are closed
products whose training methods are undisclosed `[S5][S10]`.

**Deployment posture.** We *lose* this row outright, and say so: zero production footprint `[S1]`.
Komodor and Datadog are installed in real enterprise environments at scale `[S5][S8]`. SREGym, like
us, is research substrate `[S2]`.

**Evaluation rigor.** Two honest sub-claims. *What* is graded — we lead: root cause + correct fix
+ trap, explicitly anti-reward-hacking, so a model that restarts until a metric recovers but
misdiagnoses scores 0.0 `[S1]`. *How much / external* — SREGym leads: far larger n and an external
benchmark `[S2]`. These numbers are **not head-to-head**: we have not run our policies on SREGym,
nor SREGym agents on our cascades. Vendor accuracy figures are marketing, not independently
validated `[S5][S10][S11]`.

## Where our position is honestly weaker
- **No real customers, no prod, no scale data.** Komodor cites Cisco/Dell/BlackRock; Datadog cites
  2,000+ environments. We have a test cluster `[S1][S5][S8]`.
- **Tiny n + self-grading.** 5 models × 5 incidents, an LLM-judge grading the mechanism. SREGym's
  90-problem sweep is more statistically serious `[S2]`.
- **Clean signal, not prod chaos.** We hand the model a curated diff; Bits reads RUM, profiler,
  network path, DB monitoring — messy real telemetry `[S8]`. Our trap-safety claim is only as good
  as our sim's fidelity.
- **Category gap.** A buyer comparing on-call automation will pick a deployed product; we are a
  benchmark/data engine and should be evaluated as one.

## Sources
- **S1** — `ARCHITECTURE.md`, this repo (`/Users/mei/rl/ARCHITECTURE.md`): reward formula
  (0.30·diag + 0.25·fix + 0.45·resolved − 0.60·trap), frozen-policy stance, within-group spread,
  GKE test cluster, 0.86 ceiling = escalate-the-unsolvable. *primary (self-reported)*.
- **S2** — SREGym, arXiv 2605.07161, "A Live Benchmark for AI SRE Agents with High-Fidelity
  Failure Scenarios": 90 problems, fault/noise injectors, diagnosis 38.9–72.6%, mitigation
  57.3–78.5%. https://arxiv.org/abs/2605.07161 *primary*.
- **S3** — SREGym GitHub. https://github.com/SREGym/SREGym *primary*.
- **S4** — SREGym CAIS 2026 demo, "A Live Training Ground for AI SRE Agents".
  https://www.caisconf.org/program/2026/demos/sregym/ *primary*.
- **S5** — Komodor, "Introduces Autonomous Self-Healing Capabilities" (95% accuracy; Cisco 40%
  tickets / 80% MTTR; Cisco/Dell/BlackRock).
  https://komodor.com/blog/komodor-introduces-autonomous-self-healing-capabilities-for-cloud-native-infrastructure-and-operations/
  *vendor-stated, 2025-11*.
- **S6** — GlobeNewswire, Komodor self-healing press release, 2025-11-05.
  https://www.globenewswire.com/news-release/2025/11/05/3181574/0/en/komodor-introduces-autonomous-self-healing-capabilities-for-cloud-native-infrastructure-and-operations.html
  *vendor-stated, 2025-11*.
- **S7** — Help Net Security on Komodor: remediate "with or without a human in the loop", 2025-11.
  https://www.helpnetsecurity.com/2025/11/05/komodor-platform-self-healing-and-cost-optimization-capabilities/
  *third-party-review*.
- **S8** — Datadog, "Introducing Bits AI SRE, your AI on-call teammate": investigates against
  live telemetry, human-in-the-loop triage.
  https://www.datadoghq.com/blog/bits-ai-sre/ *vendor-stated*.
- **S9** — Datadog press release, "Launches Bits AI SRE Agent": 2,000+ environments, tens of
  thousands of investigations.
  https://www.datadoghq.com/about/latest-news/press-releases/datadog-launches-bits-ai-sre-agent-to-resolve-incidents-faster/
  *vendor-stated, 2025-12*.
- **S10** — Datadog engineering, "How we built a real-world evaluation platform for autonomous SRE
  agents at scale": internal benchmark on proprietary labeled customer incidents.
  https://www.datadoghq.com/blog/engineering/bits-ai-eval-platform/ *vendor-stated*.
- **S11** — Datadog, "Meet the new Bits AI SRE: Deeper reasoning, twice as fast": ~2× faster /
  more accurate on internal benchmark, 2026-03.
  https://www.datadoghq.com/blog/bits-ai-sre-deeper-reasoning/ *vendor-stated, 2026-03*.
