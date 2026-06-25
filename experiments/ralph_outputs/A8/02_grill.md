# A8 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial takes
- **SMR:** Held-out novelty is the whole ballgame for credible eval. But "no
  training data touches it" must be defined on the *generative process*, not just
  the string id. If train and test share the same failure_class + same gold fix
  tool, the policy can memorize a class→tool mapping and look like generalization.
- **PSRE:** From an incident-response view, the meaningful novelty axis is the
  *causal mechanism* and the *organization/source*. Real post-mortems (cloudflare,
  github, slack) are public; if the model saw the cloudflare 1.1.1.1 incident in
  training, a renamed cloudflare incident in test is contaminated even if the YAML
  differs.
- **REV:** I will reject any paper that claims novelty via filename. Show me the
  contamination *definition*, the *measured* overlap, and a *re-runnable* guard.
  Also: what is the held-out N? If it's 3 incidents, your CI is meaningless.
- **RLE:** Practically, the trajectories.jsonl uses a different id namespace
  (`011-bad_deploy_errors`) than cidg (`checkout_bad_rollout`). If you only match
  ids you'll declare everything novel and be wrong. Map on semantics.
- **DVO:** Make the check a CI gate that runs fast, exits non-zero on overlap, and
  is independent of the builder so a hand-edited manifest still gets caught.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree with making failure_class a *hard* exclusion. The
  curriculum deliberately reuses ~15 failure classes; if you exclude every seen
  class you hold out essentially nothing and can't measure within-class
  generalization, which is the interesting quantity. Novelty should be at the
  *instance/source* level, not the class level.
- **SMR → RLE:** Pushing back — if you keep seen classes you must at least *report*
  the class overlap, else REV nukes you for "near-duplicate" leakage. Compromise:
  class overlap is a recorded flag with a `--strict-class` switch, not silently
  ignored.
- **PSRE → REV:** Disagree that small N is automatically fatal. 13–15 genuinely
  unseen incidents spanning simple synthetic + novel real-world (knight capital,
  facebook bgp, kafka poison pill) is a legitimate stress set; SRE eval is about
  coverage of mechanisms, not Monte-Carlo CI width.
- **REV → PSRE:** I'll concede coverage matters, but then you MUST stratify the
  manifest by family so a reader sees it's not 15 trivial synthetic cases.
- **DVO → SMR:** Disagree with embedding the criterion only in a research script.
  If the guard isn't standalone and independently re-derives the train set, the
  manifest can rot. Two files, not one.

## Round 3 — synthesis
- Novelty is enforced at **Tier 1 (exact id + significant token-pair)** and
  **Tier 2 (company/vendor identity axis, HARD)**. **Tier 3 (failure_class)** is a
  recorded flag, optionally hard via `--strict-class`. (SMR+RLE compromise.)
- Match on **semantics/tokens**, not the divergent id namespaces. (RLE)
- Ship **two** scripts: builder + independent guard with a negative control. (DVO)
- Manifest is **stratified by family** and records training stats + a sha256 so a
  reviewer can audit and the gate is re-runnable. (REV)
