# F7 — 04 Spec

## Artifacts

### A. `artifacts/rebuttal_anticipation.md`
Markdown document. Required sections (validator checks H2 headers verbatim):
- `## Top-line: the two rejections to plan for`
- `## The attacks` (contains attacks A1..A10 as H3 `### A<n> — <title>`)
- `## Concession ledger`
- `## What would actually sink the paper`

Each attack (H3 block) MUST contain these labeled lines:
- `**Steelman.**` — the strongest version of the attack.
- `**Honest response.**` — the best truthful mitigation (no overclaiming).
- `**Probability.**` one of {High, Medium, Low} — likelihood a reviewer raises it.
- `**Depth.**` one of {Fatal-if-true, Serious, Manageable} — damage if it lands.
- `**Closing evidence.**` — what concrete artifact/experiment would neutralize it.

### B. `artifacts/attacks.json`
```json
{
  "project": "SRE-Degrees",
  "n_attacks": 10,
  "attacks": [
    {"id": "A1", "title": "...", "theme": "small_n|synthetic_data|flat_rft|reward_hacking|single_domain|fixed_point|reproducibility|judge_circularity|construct_validity|generality",
     "probability": "High|Medium|Low", "depth": "Fatal-if-true|Serious|Manageable",
     "one_line_response": "..."}
  ]
}
```
Required: the union of `theme` across attacks MUST include all five dispatch-mandated themes:
`synthetic_data`, `small_n`, `flat_rft`, `reward_hacking`, `single_domain`.

### C. `artifacts/validate_attacks.py`
Python 3.13 stdlib (`json`, `re`, `sys`, `pathlib`). Functions:
- `load_attacks(path) -> dict` — parse attacks.json, raise on malformed.
- `check_themes(data) -> list[str]` — return missing mandatory themes ([] = ok).
- `check_doc(md_path, data) -> list[str]` — return list of problems:
  - all four required H2 sections present,
  - one `### A<n>` per attack id in attacks.json,
  - each attack block contains all 5 labeled lines,
  - `n_attacks` in [8,12] and equals len(attacks).
- `main()` — print PASS/FAIL summary, `sys.exit(0)` iff no problems.

### Test cases (run in step 07)
1. `attacks.json` parses and has 8–12 attacks.
2. `check_themes` returns [] (all 5 mandatory themes present).
3. `check_doc` returns [] (structure intact, every attack rendered, all labels present).
4. Negative control: temporarily drop a theme in an in-memory copy → `check_themes` reports it.

## Content contract (the 10 attacks, fixed)
A1 small_n · A2 construct_validity · A3 synthetic_data (reconstruction leakage) ·
A4 flat_rft · A5 reward_hacking · A6 fixed_point (0.86) · A7 single_domain ·
A8 judge_circularity · A9 reproducibility (gateway pinning) · A10 generality (REx = known idea).
