# SRE-Degrees: A Verifiable RL Environment for Safe Incident Response

**Frozen, swappable LLM policies · a root-cause-aware reward · a searched safety verifier**

> One-line thesis: a real production cascade misleads even frontier models on the first try;
> a reward that grades **root cause + correct fix + trap-avoidance** (not just "did it come
> back up") produces trajectory data with genuine within-group signal. [src: ARCHITECTURE.md]

---

## Motivation

Real outages are **cascades**: the *loudest alert points at a victim, not the cause*, and the
*naive fix makes it worse* (scale a crash-looping control plane → it herds its datastore →
worse). "Did the metric recover?" is a reward-hackable signal — a model can restart/scale into
a green dashboard while misdiagnosing the mechanism and tripping the trap. We need an
environment where **being right about the mechanism** is what scores. [src: ARCHITECTURE.md]

## The Cascade (worked example)

Reconstructed from real post-mortems (AWS DynamoDB DNS, Cloudflare WAF, CrowdStrike CF291,
Railway/GCP suspension, Azure DDoS). [src: ARCHITECTURE.md]

- **Loud alert:** fires on the downstream **victim** service.
- **Hidden root cause:** an upstream config-crash / dependency failure.
- **Trap:** the obvious remediation (scale/restart the victim) amplifies the cascade.
- **Correct fix:** address the upstream cause; if no safe fix exists, **escalate** — don't flail.

One declarative spec drives both an in-process sim and a live cluster; cascades are *derived*,
never scripted. [src: sim/engine.py · scenarios/cidg/generated]

## Environment (the contribution that survives ablation)

A **verifiable** incident-response environment + a **self-generalizing searched verifier**:
- Within-group reward spread **0.0 / 0.15 / 1.0** — the property that makes the data trainable.
  [src: ARCHITECTURE.md]
- The safety verifier is **learned, not hand-written**: a Thompson-tree search over
  rules-as-data (no LLM code execution) discovers the safety harness. Trained on **7**
  incidents, it gates **3 held-out** incidents at **0.90 accuracy vs 0.95 hand-written**, and
  compresses **14 → 3** general rules with **zero synthesis-quality misses**.
  [src: docs/headline_insights.md · rex/harness_synth.py]

## Method (the reward + the loop)

**Reward (anti-gaming, the crux):**

```
score = 0.30·diagnosis_correct + 0.25·correct_fix + 0.45·resolved − 0.60·trap   (clamp 0..1)
```

`resolved` alone is only 45% — misdiagnose or trip the trap and you score **0.0**.
`diagnosis_correct` is an LLM-judge on the **mechanism** (a config-crash diagnosed as
"resource exhaustion" is wrong). [src: rex/scoring.py · ARCHITECTURE.md]

**REx loop:** wrap a *frozen* model — propose → harness feedback → refine, behind a safety
gate that blocks unsafe actions. No fine-tuning of the policy. [src: rex/loop.py · rex/frontier.py]

## Two-tier reality contract (honest)

- **Tier-A — sim** (`sim/engine.py`): free, deterministic, seedable; generates the bulk of
  trajectories; **one-command reproducible**.
- **Tier-B — M-real GKE** (`mreal/`): real services calling over HTTP; Prometheus/Alertmanager
  fire on the victim; **validates the mechanism** (faulting one node propagates to a downstream
  victim on a real cluster). We do **not** claim Tier-A numbers equal cluster numbers beyond
  the pinned mechanisms. [src: ARCHITECTURE.md · docs/ENVIRONMENT_DESIGN.md]

## Benchmark

- **Catalog:** 9 CIDG generated incidents + reconstructed real-outage cascades; a difficulty
  gradient from single-leaf (loud alert = cause) to multi-hop cascades (loud alert = victim).
  [src: scenarios/cidg/generated · opensre-traj/specs/real]
- **Models:** 5 frozen frontier policies across 4 providers behind one interface
  (Claude Opus 4.8 / Haiku 4.5, gpt-5.5, gemini-3.1-pro, deepseek-v4-pro via the HUD gateway).
  [src: agent/llm.py · ARCHITECTURE.md]
- **One-shot honest band:** lands in the **20–50%** reward band with real variance and cleanly
  separates weak from strong: **haiku 0.27 vs opus 0.50** mean. [src: docs/headline_insights.md]

## Results

**Frontier sweep — REx as a deployment wrapper (demo claim).** Same 5 incidents, same reward,
baseline = one zero-shot answer. [src: ARCHITECTURE.md]

| Model | Provider | Baseline | REx | Lift |
|---|---|---|---|---|
| claude-haiku-4-5 | Anthropic | 0.63 | 0.86 | +0.23 |
| gpt-5.5 | OpenAI (gw) | 0.63 | 0.86 | +0.23 |
| gemini-3.1-pro | Google (gw) | 0.75 | 0.86 | +0.11 |
| deepseek-v4-pro | DeepSeek (gw) | 0.81 | 0.86 | +0.05 |
| claude-opus-4-8 | Anthropic | 0.81 | 0.86 | +0.05 |

All five frozen models converge to **0.86 = the *designed* safe ceiling** = (4×1.0 + 0.30)/5:
solve the 4 solvable incidents and **correctly escalate** the 1 unsolvable one
(`singleton_node_notready`, no safe fix). Small + REx (haiku 0.86) > opus zero-shot (0.81).

**⚠ Rigor check — ablation (equal-weight, honest).** A fair-control test shows the headline
REx lift was mostly **oracle-feedback leakage**: strip the root-cause hint and REx **0.25 ≈
zero-shot 0.24**; best-of-N **0.24** and outcome-only retry **0.23** add ~0. So the defensible
contributions are the **verifiable environment** and the **searched verifier**, not the
refinement loop itself. [src: docs/headline_insights.md · rex/runs/ablation.json]

## Takeaways

1. You can improve models at anything you can **verify** — and here the *verifier itself* is
   searched, not hand-written, and **generalizes** to held-out incidents (0.90 vs 0.95).
2. A root-cause-aware reward + a trap penalty gives **within-group signal** (0.0/0.15/1.0)
   that "did it come back up?" cannot. [src: ARCHITECTURE.md]
3. As a deployment wrapper, REx converges 5 frozen models to the safe ceiling and **escalates
   instead of flailing** on the unsolvable incident. [src: ARCHITECTURE.md]
4. Honest ablation moved the rigor to the **env + verifier**; we report it at equal weight.
   [src: docs/headline_insights.md]
5. Two-tier contract: sim numbers are reproducible; the GKE tier validates the *mechanism*,
   not the magnitudes. [src: ARCHITECTURE.md]

## Reproduce

```
HUD_API_KEY=… python3 -m rex.frontier      # frontier sweep
python3 -m rex.harness_synth               # searched safety verifier
# ablation: rex/runs/ablation.json ; design: docs/ENVIRONMENT_DESIGN.md
```

*Poster source: `experiments/ralph_outputs/F13/artifacts/poster.md`. Final raster (300dpi) /
CMYK conversion is a downstream design step.*
