# G6 — SUMMARY

**Task:** Analyze Datadog Bits AI SRE — claims, gaps, and how our graduation framework
differentiates. Be fair and sourced.

**Deliverable:** A sourced claims-and-design analysis (`artifacts/bits_ai_sre_analysis.md`)
backed by a machine-checkable citation graph (`sources.json` + `claims_table.csv`) and a hard
validator (`validate.py`, exits 0).

## Findings

**Datadog claims (sourced):** autonomous, no-prompt, hypothesis-driven RCA grounded in
thousands of incidents; proposes code fixes before you open your laptop; 8+ data sources;
~2x faster (3-4 min) investigations; "up to 95%" MTTR reduction; tested on 2,000+ customer
environments; GA, RBAC, HIPAA. [S1-S6]

**Where Bits leads (conceded):** production scale, signal breadth, enterprise hardening, speed.

**Gaps - fairly bucketed:**
- Acknowledged: human-in-the-loop (engineers review before action). [S1]
- Not disclosed: no precision/recall, no judge-human agreement, no false-positive rate, no
  public held-out adversarial benchmark with labels (benchmark shown only as a relative bar
  chart). [S2]
- Structural: trap-avoidance not publicly evaluated; online learning = non-reproducible
  moving target; graduation (escalate when no safe fix exists) not a published axis. [S1,S5]

**Our differentiation (code-cited):** mechanism-level deterministic reward where "resolved"
alone = 0.45 so confident-but-wrong RCA scores 0.0 (rex/scoring.py, 0.30/0.25/0.45/0.60);
explicit -0.60 trap penalty; graduation/escalation on the held-out no-safe-fix incident
singleton_node_notready (rex/harness.py, rex/loop.py, rex/escalate.py); emergent adversarial
cascades + frozen policy for reproducible eval (sim/engine.py, agent/llm.py, ARCHITECTURE.md).

**Verdict:** complementary - Bits ships incident response at scale; SRE-Degrees is the
reproducible, root-cause-aware evaluation harness for the victim-vs-cause class Datadog has
not publicly evaluated.

**Validation:** VALIDATE PASS (6 sources, 18 claims, all 5 types, all 6 repo files present).

**Honest limit:** claims/design analysis, not an empirical head-to-head (we did not run Bits).

**Shared-core compliance:** no core files edited; all output under G6/.
