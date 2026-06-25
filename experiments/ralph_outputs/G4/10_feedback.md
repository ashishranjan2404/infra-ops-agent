# 10 — Feedback for the next task

Grounding-before-claiming paid off: extracting the trap data from the real YAMLs immediately
exposed that 48/51 traps are a single tool (`scale_deployment`), which reframed the
contribution from "rich taxonomy" to "labeling scheme + seed taxonomy" and pre-empted the
reviewer's strongest attack — do the data pull *first*, let it set the claim's altitude.
When comparing against external benchmarks (SREGym/ITBench/AIOpsLab) the cleanest delta was
*reward-hacking guard vs trap penalty*: those are easy to conflate, and naming the
distinction precisely is where the novelty actually lives. Two reusable moves for downstream
tasks: (1) parse core constants/feedback tables out of `rex/scoring.py` via `ast` instead of
importing — keeps the artifact read-only and parallel-safe while staying grounded in real
values; (2) always attach an explicit "evidence scope" caveat when one side of a comparison
is code-grounded and the other is paper-grounded, so the novelty claim is dated and
falsifiable rather than absolute. A natural follow-on task: broaden trap diversity in the
scenario generator (premature failover, mid-incident cache flush, primary restart, blind
rollback) and run an ablation that measures whether the trap penalty changes agent behavior
vs a resolved-only oracle — that is the missing experiment that would turn this from a
labeling scheme into a validated contribution.
