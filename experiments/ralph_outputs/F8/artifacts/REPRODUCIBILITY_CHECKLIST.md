# Reproducibility Checklist — SRE-Degrees / REx

**Project**: SRE-Degrees / REx (code-as-policy incident-diagnosis harness over *frozen*
LLMs — no model weights are trained for the core results).
**Git SHA**: `8a12b414652f6a014dac9abce1e1681067185db8`
**Python**: 3.13.7 · **Generated**: 2026-06-25 (UTC) · **License**: see `LICENSE` (repo root).
**Self-audit**: `python3 experiments/ralph_outputs/F8/artifacts/verify_repro.py` → exit 0
(13 AVAILABLE / 3 SEEDED PASS · 2 PARTIAL · 1 BLOCKED, no hard fail).

Tags: ✅ `AVAILABLE` · 🎲 `SEEDED` (control-flow deterministic, *outputs not bitwise*) ·
⚠️ `PARTIAL` · ⛔ `BLOCKED`.

## Two reproducibility tiers (read first)
This system runs *sampled, mostly closed-API* LLMs, so "reproducible" means two
different things and we report both honestly:

| Tier | What reproduces | Determinism | Status |
|---|---|---|---|
| **Replay** | re-grade committed trajectories with the deterministic judge | exact, given fixed inputs (empirically verified: `repro.replay_double_grade` PASS) | ✅ |
| **Generation** | re-run a model through the harness | only the *distribution* — mean ± std over seeds; control flow seeded, LLM sampling **not** bitwise | 🎲 |

Bitwise reproducibility of an API model is impossible (providers patch silently); the
durable anchor is the **committed trajectory dataset**, not live re-generation.

---

## 1. Code
| Item | Status | Evidence | Honest note |
|---|---|---|---|
| Public code for all results | ✅ | `README.md`, `ARCHITECTURE.md`, `rex/`, `sim/`, `agent/`, `opensre-traj/` | Single repo; remote `infra-ops-agent`. |
| Runnable entrypoints documented | ✅ | `rex/eval_pass_at_k.py` (has `--model/--per-family/--seeds`), `rex/ablation.py`, `rex/README.md` | `python3 -m rex.eval_pass_at_k --frontier --per-family 2 --seeds 3`. |
| Dependencies pinned | ✅ | `requirements-rex.txt` (runtime: pyyaml, requests, matplotlib, numpy) vs `requirements.txt` (GPU/SFT: unsloth, trl) | Two stacks — runtime needs only `requirements-rex.txt`; don't install the GPU stack to run evals. |
| Environment | ✅ | Python 3.13.7; `yaml`, `requests` importable (verified) | No container/lockfile; versions are `>=`, not `==` (minor drift risk). |
| Control-flow determinism | 🎲 | `rex/tree.py:30,67` `random.Random(seed)`; `rex/loop.py` | Seeds fix tree traversal & sampling order, **not** LLM token output. |

## 2. Data
| Item | Status | Evidence | Honest note |
|---|---|---|---|
| Graded trajectory dataset committed | ✅ | `opensre-traj/out/hud_trajectories.jsonl` (tracked; **197 rollouts**) | Measured contents: claude-opus-4-8 ×68, claude-haiku-4-5 ×68, kimi-k2p5 ×61. |
| Data provenance / schema | ✅ | `opensre-traj/DATA.md`, `opensre-traj/SCHEMA.md`; rollouts from `hud_env*.py` via HUD v6 | Per-record subscores + weights documented. |
| Base scenario corpus committed | ✅ | `scenarios/cidg/*.yaml` (10 hand-written, tracked) | Real incident YAMLs (gcp/crowdstrike/cloudflare/etc.). |
| SIMPLE-tier scenarios reproducible-by-construction | ✅ | `rex/curriculum.py:77 generate_simple()` (deterministic, in-code) | 15 single-leaf incidents regenerated from code, no external data. |
| Free-form generated scenarios | ⚠️ | `scenarios/cidg/generated/*.yaml` exists on disk (53 files) but is **UNTRACKED in git** | **Dead on a fresh clone.** No committed generator+seed found for these specific files. *Fix: commit the 53 YAMLs OR the generator+seed.* |
| Doc/data drift | ⚠️ | `opensre-traj/DATA.md` advertises only the Claude half (60) + "pending glm/minimax" | Stale: committed file actually holds 197 rollouts incl. kimi-k2p5. Trust the file, not the doc. *Fix: refresh DATA.md.* |

## 3. Model weights
| Item | Status | Evidence | Honest note |
|---|---|---|---|
| Model roster / versions pinned | ✅ | `agent/models.py` ROSTER: `claude-haiku-4-5-20251001`, `claude-opus-4-8`, `gpt-5.5`, `gemini-3.1-pro-preview`, `deepseek-v4-pro`, `grok-4.3`, `glm-5p2`, `minimax-m3` | Dated/version strings recorded; weights are **closed** → version-pinned but **not weight-reproducible** (providers may patch). Best-effort; committed transcripts are the fallback. |
| Open-model training recipe | ✅ | `opensre-traj/train_rft.py`, `train_rft_v2.py` (GRPO/RFT via HUD Tinker, Qwen fork) | Recipe + CLI documented; additive, doesn't touch env/rex. |
| Trained checkpoint committed | ⛔ | none — no `*.safetensors/*.pt/*.bin` in repo (verified) | **BLOCKED**: requires `HUD_API_KEY` + GPU + a forked Qwen slug; no weights shipped. Core paper results don't depend on it (frozen-LLM design). |
| Judge model pinned per metric | ✅ | `rex/scoring.py:79` `deterministic_judge` (reproducible), `:100 hybrid_judge`, `:141 _llm_judge` (not reproducible) | **Record which judge backs each reported number.** Deterministic judge → replay-reproducible; LLM/hybrid judge → stochastic. |

## 4. Randomness & seeds
| Item | Status | Evidence | Honest note |
|---|---|---|---|
| Seeds plumbed through pipeline | 🎲 | `rex/tree.py` `seed=0` default; `rex/eval_pass_at_k.py --seeds`; `rex/ablation.py SEEDS` (3 seeds) | Job = (condition, incident, seed); checkpointable. |
| Deterministic grading available | ✅ | `rex/scoring.py:79`, `:89 mechanism_score`; empirically stable (`repro.replay_double_grade` PASS) | Pure keyword/stem matching; same inputs → same score. |
| Multiple seeds + error bars | ✅ | `ablation.py` aggregates "mean ± std over 5 incidents × 3 seeds (15 values)" | Claims are statistical, not single-run. |
| Sources of nondeterminism named | 🎲 | LLM sampling (API), provider drift, `no_temperature` reasoning models | Generation tier reproduces *in distribution* only — stated as a limitation, not hidden. |

## 5. Compute & licensing
| Item | Status | Evidence | Honest note |
|---|---|---|---|
| Hardware to reproduce | ✅/⛔ | Evals: any CPU box (no GPU). Open-model training: GPU + HUD Tinker (⛔ not provided). | Replay/eval tiers are laptop-reproducible. |
| Compute budget reported | ⚠️ | per-call cost dominated by API; no aggregate $/GPU-hour table committed | *Fix: add a cost ledger for the headline runs.* |
| License present | ✅ | `LICENSE` (repo root) | — |
| Secrets handling | ✅ | `.env` holds `ANTHROPIC_API_KEY`, `FIREWORKS_API_KEY`, `EXA_API_KEY`; gitignored | Keys **required** for generation tier, **not committed**. |

---

## Summary
| Axis | ✅ AVAILABLE | 🎲 SEEDED | ⚠️ PARTIAL | ⛔ BLOCKED |
|---|---|---|---|---|
| Code | 4 | 1 | 0 | 0 |
| Data | 4 | 0 | 2 | 0 |
| Weights | 3 | 0 | 0 | 1 |
| Seeds | 2 | 2 | 0 | 0 |
| Compute/License | 3 | 0 | 1 | 0(½) |

## Reviewer-facing limitations (the honest part)
1. **Generation is not bitwise reproducible.** Closed sampled APIs; we report mean ± std
   over seeds. Only the committed-trajectory **replay** path is exactly reproducible.
2. **`scenarios/cidg/generated/*.yaml` (53 files) are untracked** — a fresh clone cannot
   reproduce any result that depends on them. Highest-priority fix.
3. **No trained checkpoint shipped** — open-model RFT (`train_rft.py`) is a runnable
   recipe blocked on HUD key + GPU; the core (frozen-LLM) results don't need it.
4. **DATA.md is stale** relative to the committed `.jsonl` (197 rollouts, incl. kimi-k2p5).
5. **No aggregate compute/cost ledger** committed.
6. **Closed-model weights drift**; dated version strings are best-effort, not a guarantee.

## How to reproduce (happy path)
```bash
pip install -r requirements-rex.txt
# Replay tier (no keys, exact): re-grade committed trajectories with the deterministic judge.
# Generation tier (needs keys): set -a; source ~/.zshrc; set +a
python3 -m rex.eval_pass_at_k --frontier --per-family 2 --seeds 3
# Audit this checklist against the live repo:
python3 experiments/ralph_outputs/F8/artifacts/verify_repro.py
```
