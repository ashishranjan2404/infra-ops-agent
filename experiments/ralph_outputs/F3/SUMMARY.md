# F3 — Summary

**Task.** Write the Conclusion with the "graduation not deployment" framing, grounded in the
project's graduation-framework thesis. Do not edit shared core files.

**Deliverable.** `artifacts/CONCLUSION.md` — a 929-word, validated Conclusion section that
frames the SRE-Degrees incident-response agent as **earning autonomy through graduated,
mechanism-aware, revocable evaluation** rather than being deployed. Grounded in four repo
mechanisms: (1) tiered revocable trust — `autonomous/approval/blocked` in
`tools_registry.json` ("junior engineer earning trust", README:77-79); (2) an uncrammable exam
— reward `0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap` (ARCHITECTURE.md:75); (3) a
degree program — the simple→hard curriculum (`rex/curriculum.py`); (4) escalation as a passing
grade — the argued 0.86 ceiling `(4×1.0 + 0.30)/5` = solve-4 + escalate-1
(`singleton_node_notready`).

Evidence leads with behavior (escalation; haiku+REx 0.68 > opus zero-shot 0.42; spread
0.63–0.81 compressing to a uniform 0.86); limits stated aloud — small n, LLM-judge, sim ≠
cluster, demotion designed but **not yet automated**.

**Supporting artifacts.** `claims_provenance.tsv` (9 claims → source file:line) and
`validate_conclusion.py` (stdlib structure + content + provenance drift checker).

**Tests.** Validator passes (`ALL CHECKS PASSED (7 check groups; 929 words)`); two negative
controls correctly fail. One real defect — reward formula mis-cited to README instead of
ARCHITECTURE.md:75 — caught by the provenance check and fixed.

**Compliance.** No shared core file touched; all artifacts under `experiments/ralph_outputs/F3/`.

**Status:** completed.
