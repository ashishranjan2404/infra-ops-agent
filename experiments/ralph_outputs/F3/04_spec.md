# F3 — Spec

## Deliverable A: `artifacts/CONCLUSION.md`
A standalone Conclusion section in GitHub-flavored Markdown.

### Structure contract (validator-checked)
The file MUST contain, in order, headings matching these regexes:
- `^#\s+Conclusion` (H1 title)
- `^##\s+.*[Gg]raduation` (stance subsection — names the framing)
- `^##\s+What .*graduation .*real` (mechanisms subsection)
- `^##\s+.*[Ee]vidence` (evidence subsection)
- `^##\s+What .*certif` (certifies / does-not-certify subsection)
- `^##\s+.*[Cc]ohort` OR `[Ff]uture` (future-work subsection)

### Content contract
- ≥ 700 words.
- The literal phrase **"graduation, not deployment"** (or "graduation not deployment")
  appears ≥ 1×.
- Names ≥ 4 concrete repo artifacts/mechanisms from this set:
  `tools_registry.json`, `rex/scoring.py`, `rex/curriculum.py`, `ARCHITECTURE.md`,
  the trust tiers `autonomous/approval/blocked`, the safety gate, `singleton_node_notready`.
- Includes the reward expression `0.30·diagnosis + 0.25·fix + 0.45·resolved − 0.60·trap`
  (Unicode middots/minus tolerated; validator checks the coefficient tokens
  `0.30`, `0.25`, `0.45`, `0.60`).
- Includes the ceiling identity tokens `0.86` and `(4` and `0.30)/5` (the argued ceiling).
- Includes an explicit "does NOT certify" / limitations clause containing the word
  `not automated` or `not yet automated` (revocation honesty).
- No placeholder tokens: must NOT contain `TODO`, `TBD`, `FIXME`, `lorem`, `<...>`.

## Deliverable B: `artifacts/claims_provenance.tsv`
Tab-separated, header row `claim<TAB>value<TAB>source`. One row per quantitative claim.
`source` is `file:line` (or `file` for a multi-line mechanism) within the repo. Every
`value` string MUST appear literally in the cited source file (validator greps for it).

## Deliverable C: `artifacts/validate_conclusion.py`
Python 3.13 stdlib only. CLI: `python3 validate_conclusion.py`. Resolves repo root from its
own path (`.../experiments/ralph_outputs/F3/artifacts` → up 4). Checks:

1. `CONCLUSION.md` exists, ≥ 700 words, all structure regexes match in order.
2. Content contract tokens present; no placeholder tokens.
3. `claims_provenance.tsv` parses; header correct; ≥ 5 data rows.
4. For each provenance row, the repo-relative `source` file exists, and the `value` string
   appears in that file (line-checked if `:line` given, else file-wide).

Exit 0 + print `ALL CHECKS PASSED (n)` on success; exit 1 + list failures otherwise.

### Function signatures
```python
def repo_root() -> pathlib.Path: ...
def check_structure(md: str) -> list[str]:        # returns list of failure strings
def check_content(md: str) -> list[str]: ...
def check_provenance(root: pathlib.Path, tsv: str) -> list[str]: ...
def main() -> int: ...
```

## Test cases (run in step 07)
- T1: validator exits 0 on the authored `CONCLUSION.md`.
- T2: negative control — delete a required heading in a temp copy → validator exits 1 and
  names the missing heading.
- T3: negative control — a provenance row with a bogus value → `check_provenance` reports it.
- T4: `markdown` parse sanity — file has balanced headings and no stray `<...>` placeholders
  (covered by content check).
