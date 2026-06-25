# Artifact Appendix — SRE-Degrees / REx Benchmark and Evaluation Harness

*Prepared for the AAAI Artifact Evaluation (AE) track. Badge taxonomy follows the ACM
three-badge model: **Artifacts Available**, **Artifacts Evaluated — Functional**, **Results
Reproduced**.*

---

## A.1 Abstract

This artifact contains (1) **SRE-Degrees**, a benchmark of incident-response scenarios modeled
on real production postmortems (Cloudflare, Slack, GitHub, Knight Capital, AWS, …) and grouped
into three families — `simple`, `cascade`, and `novel`; (2) a deterministic **simulator**
(`sim/engine.py`) that executes a candidate remediation *plan* and reports whether the SLO is
restored and the root cause cleared; and (3) the **REx** evaluation harness
(`rex/eval_pass_at_k.py`) that runs each incident under several policies (zero-shot, best-of-N,
realistic-retry, REx with/without oracle feedback) and reports **pass@1 / pass@2 / pass@5** with
**Wilson 95% confidence intervals**, split by incident family.

The artifact lets an evaluator reproduce the paper's central claim — *REx attains higher pass@1
than non-search baselines on novel incidents, beyond sampling noise* — and verify the metric's
integrity (deterministic grading, no reward-floor leak).

The evaluation is **two-tier**:
- **Tier A (offline, free, deterministic)** — verifies the harness functions: benchmark loads,
  the deterministic judge is correct, and the reward floor does not leak. Earns **Functional**.
- **Tier B (online, costs API budget, stochastic)** — runs the full pass@k sweep using an LLM
  *proposer*. Earns **Results Reproduced**.

---

## A.2 Artifact check-list (meta-information)

| Field | Value |
|---|---|
| **Algorithm** | REx (refinement-tree search over candidate remediation plans) vs zero-shot / best-of-N / realistic-retry |
| **Program** | Python; entrypoint `rex/eval_pass_at_k.py` |
| **Benchmark data** | `scenarios/cidg/generated/*.yaml` — families `simple` (12), `cascade` (20), `novel` (10) as registered |
| **Run-time environment** | Python 3.13 (tested); macOS/Linux |
| **Hardware** | CPU-only; ~2 cores, 2 GB RAM. **No GPU.** |
| **Metrics** | pass@1 / pass@2 / pass@5 (binary pass = graded reward ≥ 0.8), Wilson 95% CI, within-group reward std |
| **Grading** | **Deterministic** keyword-set judge (`REX_JUDGE_MODE=deterministic`, default) — no LLM in the grading path |
| **Output** | JSON to `experiments/results/…json` + a printed table |
| **Experiments** | Tier A smoke (functional); Tier B pass@k sweep (reproduced) |
| **Disk** | < 50 MB |
| **Setup time** | ~2 min (venv + `pip install -r requirements-rex.txt`) |
| **Run time** | Tier A < 1 min; Tier B hours (LLM-bound) + API cost |
| **Public link** | https://github.com/ashishranjan2404/infra-ops-agent (pin a tag; mint a Zenodo DOI) |
| **License** | See repo `LICENSE` |
| **Badges claimed** | Available, Functional, Results Reproduced |

---

## A.3 Description

### A.3.1 How to access
1. Clone the repository and **check out the pinned tag/commit** used in the paper
   (development pointer is `main`; for archival reproducibility pin the camera-ready tag — at
   time of writing HEAD is `8a12b41`):
   ```bash
   git clone https://github.com/ashishranjan2404/infra-ops-agent.git
   cd infra-ops-agent
   git checkout <CAMERA_READY_TAG>   # e.g. v1.0-aaai
   ```
2. For the **Available** badge, archive the tagged release: create a GitHub Release from the tag,
   then mint a DOI by enabling the Zenodo↔GitHub integration (Zenodo snapshots the release and
   issues a citable DOI). Cite that DOI in the paper.

### A.3.2 Hardware dependencies
CPU-only. ~2 cores and 2 GB RAM are sufficient. No GPU, no accelerator, no live cluster — the
"infrastructure" is the in-process simulator `sim/engine.py`.

### A.3.3 Software dependencies
- **Python 3.13** (verified).
- Python packages: `requirements-rex.txt` (`pyyaml`, `requests`, plus `matplotlib`/`numpy` for
  the optional charting in `rex/chart.py`).
- **Tier B only:** an LLM gateway. The proposer calls `agent/llm.call(model, …)`. Provide
  credentials via environment (e.g. `HUD_API_KEY`); on this project they are loaded with
  `set -a; source ~/.zshrc; set +a`. Tier A needs **no** credentials.

### A.3.4 Benchmarks (data)
The benchmark lives in `scenarios/cidg/generated/*.yaml` and is exposed through
`rex.harness.scenarios_by_family()`, which returns the registered scenarios grouped into
`simple` / `cascade` / `novel`. Each scenario declares the gold root-cause mechanism, the correct
fix, and **traps / red herrings** so a policy that "does something plausible but wrong" is
penalized. Grading is performed by the deterministic judge in `rex/scoring.py`.

---

## A.4 Installation

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements-rex.txt
# sanity: the benchmark registry loads
python3 -c "from rex.harness import scenarios_by_family as f; print({k:len(v) for k,v in f().items()})"
# expected, e.g.: {'simple': 12, 'cascade': 20, 'novel': 10}
```

---

## A.5 Experiment workflow

### Tier A — Functional (offline, free, deterministic)
One command runs all functional checks (registry load, full-registry reward-floor check, and the
deterministic-judge unit tests):

```bash
bash experiments/ralph_outputs/F11/artifacts/smoke_ae.sh
```

Equivalently, the checks individually:
```bash
# (a) deterministic judge is correct
python3 -m pytest tests/test_rex_deterministic_judge.py -q
# (b) reward floor does not leak: empty plan and trap both score < 0.8
python3 -c "import sys,os; sys.path.insert(0,'experiments'); \
from rex.harness import scenarios_by_family; from rex.eval_pass_at_k import floor_check; \
print(floor_check([n for v in scenarios_by_family().values() for n in v]))"
```

### Tier B — Results Reproduced (online, costs API budget, stochastic)
Export credentials, then run the pass@k sweep. The fast reproduction (baseline vs REx across the
frontier model set) is:
```bash
set -a; source ~/.zshrc; set +a        # export the LLM gateway key
python3 -m rex.eval_pass_at_k --frontier --per-family 2 --seeds 3 --conditions zero_shot,rex
```
A single-model, all-conditions run (the full ablation):
```bash
python3 -m rex.eval_pass_at_k --model glm-5p2 --per-family 5 --seeds 5 \
    --conditions zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle
```
Runs are checkpointed (`…json.partial`); a crash mid-sweep can be resumed by re-running the same
command.

---

## A.6 Evaluation and expected results

**Tier A.** `smoke_ae.sh` exits **0** and prints:
- family counts all > 0 (e.g. `{'simple':12,'cascade':20,'novel':10}`);
- `floor_check` with `'floor_ok': True` — confirming the cheapest paths (empty plan, trap) score
  below the 0.8 threshold, so the metric is not trivially gamed;
- `pytest … test_rex_deterministic_judge.py` all green.

**Tier B.** Writes `experiments/results/frontier_pass_at_k.json` (or
`ablation_pass_at_k_<model>.json`) and prints a per-condition and per-family table of
pass@1/2/5 + mean + std + Wilson CI. The paper's claim is read from:
```
by_condition.rex.by_family.novel["pass@1"]   >   by_condition.zero_shot.by_family.novel["pass@1"]
```

**Reproduction tolerance.** Because the *proposer* is a sampled LLM (temperature 0.7), pass@1 has
Monte-Carlo noise; the *grading* is deterministic. A run **reproduces** the paper if, for the same
`--per-family` and `--seeds`, the reproduced per-condition pass@1 falls inside the camera-ready
Wilson 95% CI (reported in the paper's results table), **or** the reproduced and reported CIs
overlap, **and** the REx-over-baseline ordering on the `novel` family holds. *(The exact reported
figures live in the camera-ready results table; this appendix does not restate them to avoid drift —
read them from the paper and compare against the `ci95` fields the harness emits.)*

---

## A.7 Experiment customization

| Flag / env | Effect |
|---|---|
| `--model <slug>` | proposer model (e.g. `glm-5p2`) |
| `--conditions a,b,…` | subset of `zero_shot,best_of_n,retry_realistic,rex,rex_no_oracle` |
| `--per-family N` | incidents per family (`0` = all registered) |
| `--seeds N` | episodes per (condition, incident) — controls CI width |
| `--frontier` | baseline vs REx across the built-in frontier model set |
| `--max-workers N` | episode concurrency |
| `REX_JUDGE_MODE` | `deterministic` (default) / `llm` / `hybrid` |

---

## A.8 Notes / threats to reproduction

- **Simulated substrate (a feature, not a gap).** Incidents execute inside `sim/engine.py`, which
  is *deterministic given a fixed plan* (verified: the same plan scores identically across runs).
  An evaluator therefore needs **no live cluster** and grading is bit-reproducible.
- **Proposer stochasticity.** Tier B's only nondeterminism is LLM sampling; hence pass@1 is
  reported with a Wilson 95% CI and reproduction is defined by CI overlap, not exact equality.
- **Gateway model drift.** The proposer runs behind an LLM gateway. If the provider updates the
  model behind a slug, absolute numbers can shift. Pin the model slug and treat drift as a declared
  threat; the *qualitative* claim (REx > baseline on novel) is the durable result.
- **Cost & time.** Tier B is LLM-bound (hours, real API spend). Credential-free evaluators stop at
  **Functional** — this is by design; **Results Reproduced** requires the maintainer-provided key
  or the evaluator's own gateway.
- **License.** Confirm `LICENSE` in the repo permits redistribution before claiming *Available*.

---

## A.9 Badge → claim mapping

| Badge | Claim attested | Tier | How to check | Expected | Creds |
|---|---|---|---|---|---|
| **Artifacts Available** | Benchmark + sim + harness publicly & persistently archived under an open license | availability | Tagged GitHub release → Zenodo DOI; repo `LICENSE` | DOI resolves to a snapshot containing `scenarios/ sim/ rex/ experiments/ LICENSE` | no |
| **Artifacts Evaluated — Functional** | Harness installs, benchmark loads, judge correct, reward floor not leaked | offline | `bash experiments/ralph_outputs/F11/artifacts/smoke_ae.sh` | exit 0; `floor_ok=True`; judge tests green | no |
| **Results Reproduced** | REx pass@1 > baselines on `novel`, beyond sampling noise | online | `python3 -m rex.eval_pass_at_k --frontier --per-family 2 --seeds 3 --conditions zero_shot,rex` | `…rex…novel.pass@1 ≥ …zero_shot…novel.pass@1`; pass@1 within camera-ready CI / CIs overlap | yes |

The machine-readable version of this table is
`experiments/ralph_outputs/F11/artifacts/badge_claim_map.json`, validated by
`experiments/ralph_outputs/F11/artifacts/test_badge_map.py` (asserts the badge set, that every
cited evidence file exists, and that the named commands reference real modules/flags).
