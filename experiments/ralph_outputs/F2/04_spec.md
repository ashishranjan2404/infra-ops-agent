# F2 — 04 Spec

## Deliverable 1: `artifacts/LIMITATIONS.md`
A standalone markdown section, paste-ready into the paper after Results / before
Conclusion.

### Format contract
- Single `## Limitations` H2 header (so it drops into the paper outline as one section).
- Six `### LN — <title>` subsections (L1..L6).
- One closing `### Scope — what this does not invalidate` subsection.
- Every empirical claim is followed by a parenthetical source, e.g.
  `(FINAL_SUMMARY.md P4; reward 0.522→0.491)`.
- No invented numbers. Numbers must match the evidence index exactly.

### Content contract (the six limitations, with required anchor facts)
| ID | Title | Required anchor fact(s) | Source |
|----|-------|-------------------------|--------|
| L1 | Synthetic incident data | 51 generated YAMLs; authored topology/trap/fix | `scenarios/cidg/generated/*.yaml`, `build_incidents.py` |
| L2 | Oracle circularity | generator + deterministic judge co-authored; fool-rate is oracle-relative | D13 SUMMARY; `rex/scoring.py` |
| L3 | Preliminary RFT | v1 0.522→0.491 (decline); v2 0.504→0.541 (+0.037), 15 steps, 10 tasks | FINAL_SUMMARY P4 |
| L4 | Reward hacking | 5 exploit classes, hedge 92.9% fool-rate, cap 0.30 of reward | D13 SUMMARY |
| L5 | Single-domain + blocked transfer | one domain (k8s/cloud SRE); Fireball P7 BLOCKED, never pushed | CLAIMS_EVIDENCE, FINAL_SUMMARY P7 |
| L6 | Stat power / single-model / repro | ablation 0.23–0.25 indistinguishable; partial 750-ep run (API latency); single-model diagrams | FINAL_SUMMARY P3, CLAIMS_EVIDENCE |

## Deliverable 2: `artifacts/evidence_index.md`
Table mapping each limitation Ln → the repo file(s) + the exact fact lifted, for
auditability. Columns: `Limitation | Anchor fact | Source file | Verified?`.

## Deliverable 3: `artifacts/check_limitations.py`
Stdlib-only Python. Behavior:
- `CITED_FILES`: list of repo-relative paths referenced by LIMITATIONS.md.
- For each: assert it exists under repo root (`/Users/mei/rl`); for the glob
  `scenarios/cidg/generated/*.yaml`, assert count ≥ 30.
- Parse-check `LIMITATIONS.md`: read it, assert it contains the `## Limitations`
  header and all of `L1`..`L6` plus the `Scope` subsection.
- Exit 0 with a printed report if all pass; exit 1 listing failures otherwise.

### Function signatures
```python
def repo_root() -> Path: ...
def check_cited_files(root: Path) -> list[str]:   # returns failures
def check_section(limits_md: Path) -> list[str]:  # returns failures
def main() -> int: ...
```

### Test cases (manual, recorded in 07)
1. All cited files present → exit 0.
2. Glob count ≥ 30 for generated scenarios.
3. LIMITATIONS.md contains `## Limitations`, `### L1`..`### L6`, `### Scope`.
