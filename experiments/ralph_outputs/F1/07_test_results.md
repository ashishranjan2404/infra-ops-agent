# 07 — Test Results

## T1 — Validator on the deliverable
```
$ python3 check_related_work.py
path: .../F1/artifacts/related_work.md
ok: True
required_total: 19
required_present: 19
missing: []
has_heading_2_related_work: True
subsection_count: 7
has_markdown_table: True
warn_bracket_balanced: True
word_count: 1929
PASS
exit=0
```
**Result: PASS.** All 19 required citation tokens present; `## 2. Related Work` heading
present; 7 `### 2.x` subsections (≥6 required); a valid markdown table present; brackets
balanced.

## T2 — Python syntax compile of the validator
```
$ python3 -m py_compile check_related_work.py
compile OK
```
**Result: PASS.**

## T3 — Markdown parse / structure sanity
Headings, table separator row, and list structure parse cleanly (the regex table check
in T1 requires a `|---|` separator row, which exists). No unterminated code fences.

## T4 — No shared-core edits (parallel-safety check)
```
$ git status --porcelain | grep -E "rex/|sim/|agent/|ralph_status" | grep -v ralph_outputs
```
Lines returned correspond to files already modified/deleted in the **session-start git
snapshot** (pre-existing branch state: `agent/llm.py`, `rex/scoring.py`, `sim/engine.py`,
etc.). `git diff --stat` confirms these predate this task. **I edited none of them** —
all my writes are under `experiments/ralph_outputs/F1/`. PASS.

## Fixes applied during testing
None required — validator passed on first run; the deliverable was authored to the
coverage contract in 04_spec.md, so no missing-token iteration was needed.
