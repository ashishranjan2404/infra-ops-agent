# A8 — 10 Feedback for the next task

The two training corpora (`trajectories.jsonl`, `hud_trajectories.jsonl`) and the
cidg registry use **different id namespaces** (`011-bad_deploy_errors` vs
`checkout_bad_rollout`), so any train/test split work MUST match on semantics
(tokens, company, failure_class) rather than ids — pure id-matching falsely
declares everything novel. The strongest, simplest contamination signal here is the
**company/vendor identity axis**: all 14 `cascade` incidents are public post-mortems
from companies present in training, so they are contaminated regardless of YAML
differences — the only genuinely held-out real-world incidents come from orgs absent
from training (facebook, knight capital, azure, firefox, gke, kafka). Next tasks that
need an eval set should consume `A8/artifacts/heldout_manifest.json` `held_out` (15
default, 13 strict-class) and note the **zero held-out cascade coverage** gap: if a
cascade generalization number is needed, new cascade incidents must be authored from
unseen organizations. Keep the builder+guard split (independent re-derivation +
negative control) pattern — it makes the gate trustworthy and CI-able.
