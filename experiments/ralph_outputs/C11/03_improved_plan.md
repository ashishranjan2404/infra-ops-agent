# 03 — Improved Plan

## What changed after the grill
1. **Report false-allows alongside accuracy drop** (accepted SRE+MLR). The headline metric
   stays accuracy drop (the task's explicit ask), but every rule row also reports
   `false_allows_introduced` and `false_blocks_removed` so a safety reader sees severity.
2. **Define "the 3 rules" empirically, not by fiat** (accepted REV). Before designing, I
   ran a coverage count: across 42 scenarios the block-mechanisms that fire are
   forbidden_category (dominant), leak_restart, last_ready_node, rollback_no_deploy, and
   replica_limit (never). The 3 HEADLINE rules = the three core guards that fire as is_safe
   blocks: R1/R2/R3. R4/R5 reported for completeness.
3. **Keep R4 but label it untriggered** (accepted DVO). R4_replica_limit shows 0.0 drop;
   the JSON shows 0 false-allows introduced, making "untriggered here" self-evident.
4. **Marginal-given-others, documented** (accepted RLE+REV). The ablation answers "what
   does the harness lose if this rule is deleted." First-match-wins masking is documented
   as a known property; no standalone second mode (rejected — answers a different question
   and is unrequested gold-plating).
5. **Attribution test** (accepted RLE). A test asserts each guard's reason string matches
   exactly one rule predicate, so ablation never mis-credits.

## Rejected / deferred
- **Severity-weighted ranking** (SRE wanted it as headline): rejected as headline because
  the task asks for accuracy drop and no validated severity model exists. The FA column
  carries the safety signal instead.
- **A second "standalone" ablation mode** (REV floated): rejected as scope creep; it
  answers a different question than "delete this rule."

## Final deliverable shape (unchanged paths)
`artifacts/rule_ablation.py` (+ CLI), `artifacts/test_rule_ablation.py`,
`artifacts/ablation_result.json`. No core edits.
