# D13 — 03 Improved Plan

## Changes from 01, driven by the grill

**Accepted:**
- **(REV) Human-oracle + full taskset.** Added an explicit `HUMAN_ORACLE` verdict per
  attack and defined `judge_fooled = (judge_verdict != human_oracle)`. Run over **all
  42 scenarios**, report per-attack fool-rate, not a single example.
- **(RLE) Probe the composed score.** Added `run_score_probe()` calling the real
  `score_plan` with the hedge diagnosis + a *legitimate* correct fix to quantify the
  shotgun reward (hypothesis: 0.55 = 0.30 diag + 0.25 fix).
- **(SRE) Hedge is the headline ops risk.** `gold_plus_all_herrings` is a first-class
  attack, oracle-labeled WRONG with inline rationale (a non-committal diagnosis leads
  an operator to the trap fix).
- **(SMR) Exploitability caveat.** `verbatim_gold_echo` is marked **informational**
  (gold text is hidden at eval → not policy-reachable). The writeup separates
  *directly-reachable* exploits (need only public symptom words) from capability-gated.
- **(DEV) Self-contained, no core edits.** Probe sets `sys.path` to repo root, forces
  `JUDGE_MODE="deterministic"`, writes its own `probe_results.json`. Touches no core.

**Rejected, with reason:**
- **(SMR) Make reachability a build target via a live RL run.** Rejected — hours of
  GPU, risks the shared GKE cluster (MEMORY: do-not-teardown), and a static probe
  already establishes the vulnerability. Logged as an explicit limitation in `09`.
- **(REV) Treat the hedge as partial credit.** Rejected per RLE: the scenario rubric
  defines herrings as wrong mechanisms with trap penalties; a co-equal hedge is
  non-committal, not partially right. Oracle stays WRONG, rationale documented.

## Final attack set (7)
hedge(`gold_plus_all_herrings`), `single_gold_token`, `negated_gold`,
`wrong_component_right_mechanism`, `homoglyph_herring_evasion` — all reachable;
`verbatim_gold_echo` — informational; `whitespace_only` — robustness guard.

## Deliverables unchanged
Probe + pytest + results JSON under `artifacts/`, plus the 10 step docs.
