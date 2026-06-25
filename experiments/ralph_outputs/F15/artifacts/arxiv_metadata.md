# arXiv Metadata — SRE-Degrees (human-readable view)

Rendered from `arxiv_metadata.yaml` (the machine-readable source of truth).

| Field | Value |
|---|---|
| **Title** | SRE-Degrees: A Verifiable Environment and a Searched Verifier for Safe Incident Remediation under Cascading Failure |
| **Authors** | TBD — fill before posting (de-anonymize). Identities are intentionally not fabricated. |
| **Primary category** | `cs.SE` |
| **Cross-list** | `cs.AI`, `cs.LG` |
| **ACM class** | I.2.6 (Learning); D.2.5 (Testing & Debugging); D.4.5 (Reliability) |
| **License** | arXiv.org perpetual non-exclusive (CC BY 4.0 = opt-in, irreversible) |
| **Comments line** | Preprint. Submitted to AAAI 2026. Code + environment available. NN pages / MM figures (fill from PDF). |
| **Journal-ref / DOI** | none (preprint) |

## Abstract (arXiv field — plain text, macro-free, ~1.5k chars)
> Automated incident remediation agents are routinely evaluated on whether they
> resolve a fault, but rarely on whether their actions are safe under cascading
> failure, where a locally-correct fix can trigger downstream outages. We present
> SRE-Degrees, a verifiable simulation environment for incident remediation built
> on a causal incident-dependency graph (CIDG), together with a searched verifier
> that scores candidate remediations for root-cause correctness rather than
> symptom suppression. The environment ships a deterministic judge and a
> reproducible pass@k harness over a suite of incident families with controllable
> cascading dependencies. Our verifier, REx, performs Thompson-sampling tree
> search over candidate refinements and routes novel incidents to escalation
> rather than guessing. Across a held-out incident set the searched verifier
> substantially improves pass@1 over a zero-shot baseline while preserving safety
> on cascading scenarios, and we report an honest ablation isolating the
> contribution of search, root-cause reward, and escalation routing. We release
> the environment, the deterministic judge, and the evaluation harness to support
> reproducible study of safe, verifiable incident remediation.

## Why these categories
- **`cs.SE` (primary):** the core contribution is a *verifiable environment + evaluation harness*
  for automated software/operations incident remediation — simulation, deterministic judge, and a
  reproducible pass@k pipeline. This is squarely software-engineering tooling and evaluation.
- **`cs.AI` (cross-list):** the **searched verifier (REx)** is a Thompson-sampling tree search with
  a novelty router/escalation handoff — an AI search/decision contribution.
- **`cs.LG` (cross-list):** pass@k evaluation methodology, reward design (root-cause vs symptom),
  and the RL-adjacent agent framing make it relevant to the learning community.

## Consistency check before posting
1. Title in YAML == `\title{}` in `F6/.../main.tex` (line-break `\\` stripped). ✔ (matches)
2. Abstract here == compiled abstract once `sections/00_abstract.tex` is written. ⚠ upstream empty.
3. Page/figure counts in `comments` filled from the actual compiled PDF. ⚠ pending PDF.
