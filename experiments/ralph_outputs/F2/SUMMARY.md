# F2 — SUMMARY: Honest Limitations section

**Task:** Write a candid, grounded Limitations section for the SRE-Degrees paper.

**Deliverable:** `artifacts/LIMITATIONS.md` — a paste-ready `## Limitations` section
with six grounded subsections + a Scope closer, every empirical claim cited.

| ID | Limitation | Anchor fact | Source |
|----|-----------|-------------|--------|
| L1 | Synthetic incidents | 42 evaluated / 51 on-disk YAMLs, all author-authored | FINAL_SUMMARY P1; scenarios/cidg/generated/*.yaml |
| L2 | Oracle circularity | reward 0.30·diag+0.25·fix+0.45·resolved, author keyword judge | rex/scoring.py:22; D13 |
| L3 | Preliminary RFT | v1 declined 0.522→0.491; v2 +0.037 over 15 steps | FINAL_SUMMARY P4 |
| L4 | Reward hacking | 5 exploit classes, hedge **92.9%** fool-rate, capped at 0.30 reward | D13 SUMMARY |
| L5 | Single-domain + blocked transfer | one domain; Fireball P7 **BLOCKED**, never pushed | FINAL_SUMMARY P7 |
| L6 | Stat power / single-model | ablation 0.23–0.25 indistinguishable; partial 750-ep run; semi-synthetic SME | CLAIMS_EVIDENCE; FINAL_SUMMARY P3 |
| Scope | Surviving results | harness 66.7%→89.7%; REx-SME 0.242→0.687 (2.8×) | table3; ablation.json |

**Verification:** check_limitations.py exits 0 — all 7 cited files exist, generated
glob = 51 (>=30), LIMITATIONS.md well-formed. Canary grep confirms 92.9% is live in
D13, not invented. Reward weights confirmed against rex/scoring.py:22.

**Artifacts (task-namespaced, no core edits):**
- artifacts/LIMITATIONS.md (deliverable, 115 lines)
- artifacts/evidence_index.md (14-row audit table)
- artifacts/check_limitations.py (stdlib validator, exit 0)

**Status:** completed. No shared core file touched.
