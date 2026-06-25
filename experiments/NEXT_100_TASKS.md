# SRE-Degrees — Next 100 Tasks (Categorized)

Generated from analysis of the AAAI 2026 paper draft + meeting action items +
competitive landscape (SREGym) + reviewer-anticipation gaps.

---

## CATEGORY A: Benchmark & Data (18 tasks)

A1.  Run the full 42-incident pass@k evaluation (currently only 5 incidents have pass@k)
A2.  Complete the 750-episode ablation with a faster model (vLLM local or cheaper API)
A3.  Source 10+ fully real incidents (not synthesized from postmortems) — outreach to companies
A4.  Reach out to Snorkel for incident logs (RL company, referenced in paper)
A5.  Reach out to CircleCI, incident.io, Cloudflare for anonymized incident data
A6.  Convert 10 remaining danluu postmortems into scenario YAMLs (Facebook, Knight Capital, etc.)
A7.  Add incident difficulty scoring (metadata: expected_pass_rate, trap_complexity)
A8.  Create a held-out test set that NO training data touches (strict novelty)
A9.  Label each incident with MTTR from the real postmortem (for correlation analysis)
A10. Add blast-radius metadata to each incident (how many services affected)
A11. Create incident pairs (same root cause, different symptom) for transfer testing
A12. Build a curriculum ordering (easy→hard) for curriculum learning experiments
A13. Add multi-fault incidents (2 simultaneous faults) — currently all single-fault
A14. Add time-pressure variants (budget-limited episodes) for realistic eval
A15. Create a "noisy metrics" variant (alerting degrades) per the assertion schema
A16. Validate all 42 scenarios with the sim engine (fix_resolves must be true)
A17. Create a data card / datasheet for the benchmark (for AAAI reproducibility)
A18. Upload dataset to HuggingFace with proper metadata

## CATEGORY B: Evaluation & Metrics (15 tasks)

B1.  Run pass@k on all 42 incidents × 5 conditions × 5 seeds (the full grid)
B2.  Compute McNemar's paired test for all condition pairs (paper claims it, hasn't run)
B3.  Compute Wilson 95% CIs for all pass@k numbers
B4.  Split pass@k results by incident type (simple/cascade/novel) — 3 separate tables
B5.  Run the frontier sweep with pass@k (currently only mean reward for 5 models)
B6.  Add trap-action avoidance rate as a standalone metric (not just embedded in reward)
B7.  Add root-cause accuracy as a standalone metric (separate from pass/fail)
B8.  Compute effect sizes (Cohen's d) for all claimed lifts
B9.  Run bootstrap confidence intervals (10000 resamples) as robustness check
B10. Create a learning curve (pass@1 vs training steps) for the RFT run
B11. Run ablation with multiple thresholds (0.7, 0.8, 0.86, 0.9) to show robustness
B12. Add per-incident pass@k breakdown (which incidents are solvable, which aren't)
B13. Compute inter-annotator agreement on the deterministic judge (if humans relabel)
B14. Create a cost-normalized metric (pass@1 per dollar of API spend)
B15. Compare pass@1 directly against SREGym leaderboard numbers

## CATEGORY C: Harness Synthesis (12 tasks)

C1.  Run harness synthesis with different complexity penalties (lambda sweep)
C2.  Run harness synthesis on only cascade incidents (does it find different rules?)
C3.  Run harness synthesis on only novel incidents (generalization test)
C4.  Analyze the 3 synthesized rules — are they interpretable? Write rule explanations
C5.  Compare synthesized rules against hand-written rules line-by-line (what's missing?)
C6.  Run harness synthesis with different base models (does the proposer matter?)
C7.  Test harness transfer: synthesize on simple, evaluate on cascade (cross-type)
C8.  Add a 4th rule candidate (can we push past 89.7%?)
C9.  Run harness on the full 42 incidents (currently trained on 7, tested on 3)
C10. Measure harness inference latency (does is_safe add meaningful overhead?)
C11. Create a rule-ablation (remove each of the 3 rules, measure accuracy drop)
C12. Write a formal proof or argument for why 3 rules is sufficient (information-theoretic)

## CATEGORY D: RLVR / Training (14 tasks)

D1.  Run RFT for 50+ steps (currently only 15-25) to see if +0.037 trend continues
D2.  Run RFT with Qwen-14B (meeting request — 8B may be too small)
D3.  Run RFT with same-scenario GRPO groups (the third fix from Table 1)
D4.  Run RFT with the harness in the loop (Wenji's ask — LLM+harness, not LLM alone)
D5.  Compare RFT vs SFT on the same data (which gives bigger gains?)
D6.  Run DPO instead of GRPO (preference pairs from override data)
D7.  Train on cascade incidents only (does it hurt simple? helps cascade?)
D8.  Train on Fireball data (Claim 2 — needs Wenji's data pushed)
D9.  Run curriculum learning (easy→hard ordering)
D10. Run RFT with different reward weightings (sweep W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY)
D11. Measure training stability (variance across random seeds for the RFT run)
D12. Run RFT with group size 8 (currently 4) — does more rollouts help?
D13. Test reward hacking: does the model find ways to game the deterministic judge?
D14. Run RFT on the 42-incident benchmark (currently only 10 tasks)

## CATEGORY E: Fireball / Cross-Domain Transfer (10 tasks)

E1.  Get Wenji's GRPO branch pushed to the repo
E2.  Get the FIREBALL D&D trajectory dataset (incidents.jsonl)
E3.  Run Fireball-trained vs OpenSRE-trained vs zero-shot on 14 cascade incidents
E4.  Run Fireball-trained vs OpenSRE-trained on 8 simple incidents (does it hurt?)
E5.  Run Fireball transfer on 10 novel incidents (generalization test)
E6.  Ablate Fireball: full trajectories vs state-only vs action-only
E7.  Test transfer from other game domains (not just D&D — e.g., text adventure games)
E8.  Measure how much Fireball data is needed (1k? 10k? 50k trajectories?)
E9.  Compare Fireball transfer vs synthetic SRE data augmentation (which helps more?)
E10. Write the Fireball transfer section of the paper (currently blocked)

## CATEGORY F: Paper Writing & Submission (15 tasks)

F1.  Write the full Related Work section (currently thin — add CWM, AutoHarness, REx citations)
F2.  Write the Limitations section honestly (synthetic data, single-domain, preliminary RFT)
F3.  Write the Conclusion with the "graduation not deployment" framing
F4.  Create publication-quality figures (matplotlib + the Chrome-rendered tables)
F5.  Write the Abstract (currently draft — tighten to 250 words for AAAI)
F6.  Format paper for AAAI 2026 template (LaTeX, specific page limits)
F7.  Write a rebuttal-anticipation doc (what will reviewers attack?)
F8.  Create a reproducibility checklist (code, data, model weights, seeds)
F9.  Write the supplementary material (full incident catalog, all YAML specs)
F10. Get all co-authors to sign off on claims (Ashish, Wenji, Sylvie)
F11. Create the artifact evaluation appendix (for AAAI artifact track)
F12. Write a 2-page summary for non-academic audience (for YC/fundraising)
F13. Create a poster version (for conference presentation)
F14. Prepare a 15-minute talk outline (for AAAI presentation if accepted)
F15. Submit to arXiv as preprint (before AAAI deadline for priority)

## CATEGORY G: Competitive Analysis & Positioning (8 tasks)

G1.  Run SREGym benchmark with our agent (direct comparison on their 90 problems)
G2.  Run our benchmark with SREGym's Stratus agent (reverse comparison)
G3.  Analyze SREGym's pass@1 leaderboard — where would we rank?
G4.  Compare our trap-action labels vs SREGym's (do they have anything similar?)
G5.  Write a positioning matrix (us vs SREGym vs Komodor vs Datadog Bits AI)
G6.  Analyze Datadog's Bits AI SRE blog — what do they claim? What can't they do?
G7.  Track Resolve.ai's product updates (closest commercial competitor)
G8.  Write a "why we're different" one-pager for investors/partners

## CATEGORY H: Infrastructure & Tooling (10 tasks)

H1.  Set up vLLM locally for faster eval (avoid API latency — the ablation stalling issue)
H2.  Create a CI pipeline for the eval suite (run pass@k on every PR)
H3.  Containerize the eval pipeline (Docker for reproducibility)
H4.  Set up W&B / Trackio experiment tracking for all runs
H5.  Create a dashboard for live experiment monitoring (the promotion-engine dashboard)
H6.  Build a scenario validator (CI check: every YAML must pass sim engine)
H7.  Create a model registry (track all forked models, their slugs, training status)
H8.  Set up automated nightly eval (cron job that runs pass@k on latest model)
H9.  Create a leaderboard page (like SREGym's — public facing)
H10. Write a Makefile / justfile for common operations (eval, train, generate)

## CATEGORY I: Theory & Analysis (8 tasks)

I1.  Formalize the "graduation framework" concept (what does it mean to "earn autonomy"?)
I2.  Prove the trap penalty > resolved reward creates bimodality (theoretical argument)
I3.  Analyze the bimodal distribution statistically (Hartigan's dip test)
I4.  Write the information-theoretic argument for 3 rules sufficiency
I5.  Formalize the relationship between SME feedback and RLVR (when does feedback help?)
I6.  Analyze failure modes: categorize all 0-reward rollouts by failure type
I7.  Create a taxonomy of trap actions (restart-trap, scale-trap, rollback-trap, failover-trap)
I8.  Write a theoretical comparison: code-as-policy vs RLHF vs constitutional AI

## CATEGORY J: Real-World Validation (10 tasks)

J1.  Deploy the agent in a staging K8s cluster with real chaos injection
J2.  Run the agent on a live incident (shadow mode — observe, don't act)
J3.  Get 5 SREs to evaluate the agent's diagnoses (human evaluation study)
J4.  Measure real MTTR improvement (agent-assisted vs unassisted)
J5.  Create a case study: one incident end-to-end with the agent
J6.  Test the agent on a novel incident type it's never seen (true generalization)
J7.  Run the agent against the gcp-bench or linode-bench (live cloud scenarios)
J8.  Create a demo video for the paper / presentation
J9.  Get feedback from an actual on-call SRE team (not just academics)
J10. Write a "lessons from production deployment" section

---

## TOTAL: 120 tasks across 10 categories

| Category | Tasks | Priority | Blocked? |
|----------|-------|----------|----------|
| A: Benchmark & Data | 18 | P0 | No |
| B: Evaluation & Metrics | 15 | P0 | No (needs faster model) |
| C: Harness Synthesis | 12 | P1 | No |
| D: RLVR / Training | 14 | P0 | No |
| E: Fireball Transfer | 10 | P1 | Yes (Wenji's data) |
| F: Paper Writing | 15 | P0 | No |
| G: Competitive Analysis | 8 | P2 | No |
| H: Infrastructure | 10 | P1 | No |
| I: Theory & Analysis | 8 | P2 | No |
| J: Real-World Validation | 10 | P2 | No (needs cluster) |
