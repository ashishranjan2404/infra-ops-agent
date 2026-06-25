# 02 — Grill (5 personas, 3 rounds)

Personas: Senior ML Researcher (MLR), Principal SRE (SRE), AAAI Reviewer (REV),
RL Engineer (RLE), DevOps Lead (DVO).

## Round 1 — initial takes
- **MLR**: A leave-one-out ablation is the right instrument for attributing accuracy to
  components. But "accuracy" on an imbalanced action set (most actions are safe) can be
  misleading — a rule that only governs rare unsafe actions will show a tiny accuracy
  drop yet be safety-critical. Report false-allows separately, not just accuracy.
- **SRE**: For a safety gate the only number I care about is FALSE-ALLOWS (an unsafe
  action let through). A rule with 0.003 accuracy drop but that prevents draining the
  last node is not "minor" — it prevents a full outage. Accuracy drop alone undersells it.
- **REV**: What are "the 3 rules"? `is_safe` has 5 distinct guard clauses. Picking 3 needs
  justification or it looks arbitrary / cherry-picked. Define the rule set empirically.
- **RLE**: The wrapper-by-reason-string is clever but fragile. If two guards share a
  substring you mis-attribute. And "first match wins" means ablation interacts — you're
  measuring marginal-given-others, not standalone. Be explicit about which you report.
- **DVO**: Don't edit core. Good. Also: make it reproducible and runnable with one
  command and a committed JSON output, or it's not an artifact, it's a claim.

## Round 2 — react to another persona (genuine disagreement)
- **SRE → MLR**: I disagree that accuracy should headline at all. You'd rank R1
  (forbidden_category, huge accuracy drop) far above R3 (last_ready_node, tiny drop), but
  operationally R3 prevents the single worst action in the whole sim — taking the cluster
  fully down. Accuracy-drop ranking is the WRONG ranking for a safety audit.
- **MLR → SRE**: Disagree back. The task literally says "measure accuracy drop." Accuracy
  IS the requested metric; severity weighting is a different study. I'll report BOTH —
  accuracy drop as the headline (as asked) and false-allows as the safety annotation — but
  I won't smuggle in a severity model that wasn't requested and isn't validated.
- **REV → RLE**: I don't buy "first-match-wins makes it marginal-given-others, so it's
  fine." For an ablation paper that's a confound. If R1 masks R2 on some action, you'll
  under-credit R2. You must either report it's marginal-given-others (honest) or run
  standalone (each-rule-alone). Pick one and SAY it.
- **RLE → REV**: Partial concede. Marginal-given-others is the correct quantity for "what
  does the harness lose if I delete this rule" — which is the actual question. Standalone
  would answer a different question. I'll keep marginal-given-others and document the
  masking caveat explicitly rather than over-engineer a second mode nobody asked for.
- **DVO → MLR**: R4 never fires (no scenario at replica limit). Reporting a 0.0-drop rule
  could read as "useless rule." Disagree with dropping it — keep it, but LABEL it
  "untriggered in this scenario set" so we don't claim it's dead code.

## Round 3 — synthesis
Consensus:
1. Headline = accuracy drop per rule (as the task requests), but ALWAYS annotate
   false-allows-introduced next to it (SRE/MLR compromise). Severity weighting is
   out of scope but the FA column lets a reader see it.
2. Define "the 3 rules" empirically: the three guards that actually fire as blocks
   across the scenario set (R1, R2, R3). Report R4/R5 too, with R4 flagged untriggered.
3. The ablation measures marginal-given-others (delete-one); document the first-match
   masking caveat. No second mode.
4. Wrapper attribution validated by a test asserting each guard reason matches exactly
   one rule predicate (kills RLE's mis-attribution worry).
5. One-command run + committed JSON (DVO).
