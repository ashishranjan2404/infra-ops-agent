# 04 — Spec

## Deliverable: `artifacts/related_work.md`
Markdown. Required structure (the validator enforces this contract):

- A top heading matching `## 2. Related Work`.
- Subsection headings (`### 2.x ...`) for: SRE benchmarks; code-as-policy/CWM; harness
  synthesis/AutoHarness; refinement/REx; transfer/FIREBALL; RLVR/feedback; statistics.
- A markdown summary table (header row with `|` and a `---` separator row).

### Required citation tokens (coverage contract)
The validator asserts each of these substrings appears at least once (case-insensitive):

```
REQUIRED = [
  "SREGym", "AIOpsLab", "ITBench",
  "Code World Models", "CWM", "Code as Policies",
  "AutoHarness",
  "REx", "Thompson", "Reflexion", "Self-Refine",
  "FIREBALL",
  "GRPO", "RLVR", "Constitutional AI", "LLM-as-a-Judge",
  "pass@k", "Wilson", "McNemar",
]
```

### Per-citation contract (1 sentence what-it-is + borrow/new)
| token | what-it-is (accurate) | our delta |
|---|---|---|
| SREGym | 90-problem live-K8s benchmark, pass@1 leaderboard, arXiv 2605.07161 | training method, not benchmark; trap labels; cheap sim |
| AIOpsLab/ITBench | prior fault-injection SRE harnesses SREGym builds on | not searched, no SME signal |
| CWM (Meta) | model trained to predict code-execution effects → world model | external deterministic world model as verifier+grader |
| Code as Policies | LLM emits program actions (inspectable/verifiable) | plan = structured program; safety = interpreted data |
| AutoHarness | synthesize the test-harness/verifier vs hand-write | rules-as-data over fixed features; held-out acc |
| REx | bandit/Thompson-tree over refinement candidates | exact impl in rex/tree.py; SME-vs-no-oracle ablation |
| Reflexion/Self-Refine | verbal self-feedback drives next attempt | our feedback is sim-grounded + ablated oracle |
| FIREBALL | ~25k D&D sessions w/ state_before→action→state_after | D&D→SRE transfer, untested elsewhere |
| GRPO | group-relative PO (DeepSeekMath/R1) | sim reward as grader, groups for within-group σ |
| RLVR | RL from verifiable rewards (Tülu-3 line) | deterministic *diagnosis* reward |
| Constitutional AI | principles replace human prefs; model self-critiques | searched rules as a hard code gate, sim-grounded |
| LLM-as-a-Judge | MT-Bench; noisy/non-reproducible judge | we replace it w/ deterministic keyword judge |
| pass@k/Wilson/McNemar | unbiased estimator; CI; paired exact test | paired on (incident,seed); reported with p-values |

## Validator: `artifacts/check_related_work.py`
- stdlib only, `python3`.
- Reads `related_work.md`.
- Checks: (a) `## 2. Related Work` present; (b) ≥1 markdown table; (c) every REQUIRED
  token present; (d) ≥6 `### 2.` subsections; (e) no obviously-broken markdown
  (balanced `[` `]` count as a soft check).
- Exit 0 + prints `PASS` with counts; exit 1 + lists missing tokens on failure.
- Function: `check(path) -> (ok: bool, report: dict)`; `__main__` runs it on the sibling
  `related_work.md` and prints a report.
