# Abstract

Mean-time-to-resolution, not detection, dominates the cost of production incidents, and
the hardest cases are cascades: the loudest alert fires on a downstream victim while the
root cause sits upstream, so the naive fix—restart, scale, fail over, roll back—worsens
the outage. Frontier LLMs anchor on the loud symptom and emit such trap actions. We
present a methodology for training trap-aware SRE agents from public postmortems, built
around the principle that you can improve a model at anything you can verify—and that the
verifier itself can be learned, not hand-written. Three components compose: a
code-as-policy safety harness whose blocking rules are synthesized by Thompson-sampling
search over rules-as-data; a REx loop that proposes a remediation plan and checks against
a ground-truth simulator whether the SLO actually recovers; and a deterministic verifiable
reward—a keyword-set diagnosis judge replacing a noisy LLM judge, making training fully
reproducible and credit-free. Our central honest finding relocates the contribution to the
environment and the learned verifier: trained on seven incidents, the synthesized harness
gates unsafe actions on held-out incidents at roughly 0.90 accuracy versus 0.95
hand-written, compressing fourteen rules to three with zero synthesis-quality misses; its
only miss is a hazard never seen in training. Meanwhile, REx's headline lift (0.69 versus
0.24 zero-shot) is largely oracle-feedback leakage—strip the root-cause hint and it
collapses to 0.25, an explicit generalization boundary. We release the harness, simulator,
a 42-incident family-labeled benchmark, and the deterministic reward.

---

**Word count: 233** (≤250 AAAI target; counted via `sed`/`wc -w`, see 07_test_results.md)

## Provenance
- *MTTR/cascades, naive-fix-worsens, trap actions* — `experiments/PAPER_OUTLINE.md` §1.
- *Synthesized harness, Thompson search, rules-as-data* — PAPER_OUTLINE.md §3.2; `rex/harness_synth.py`.
- *~0.90 vs 0.95 hand-written; 14→3 rules; one unseen-hazard miss* — `docs/headline_insights.md` §2; `rex/runs/harness_synth.json`.
- *Deterministic verifiable reward, no LLM judge, credit-free* — PAPER_OUTLINE.md §3.4; insights theme line.
- *REx 0.69 vs zero-shot 0.24; no-oracle collapse to 0.25* — `rex/runs/ablation.json` aggregate (rex 0.687, zero_shot 0.242, rex_no_oracle 0.250); `docs/headline_insights.md` §3.
- *42-incident, 12/20/10 family-labeled benchmark from 19 postmortems* — PAPER_OUTLINE.md §4.
- *Omitted as unsupported:* C2 FIREBALL transfer (pending, outline §5.3); McNemar p-value (grid partly pending, §5).
