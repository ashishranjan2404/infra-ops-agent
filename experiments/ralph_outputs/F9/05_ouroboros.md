# 05 — Ouroboros (self-critique as 3 different engineers)

## Engineer A — Data-quality reviewer
**Problems found:**
- A1. Several files share a `meta.id` (`80-multi-cert-poolleak.yaml` and
  `80-gitlab-db-deletion.yaml` both prefix `80`; ids may also collide). If I dedup or
  index by id I silently drop incidents. → **Fix:** key on `file`, never on `id`;
  table is one row per file.
- A2. Some specs have empty `urls: []`; rendering "URLs:" with nothing is noise. →
  **Fix:** only emit URL line when non-empty.
- A3. `severity` may be int or float or absent; string-formatting must tolerate "". →
  **Fix:** guard with `if rc_sev != ""`.

## Engineer B — Markdown/format reviewer
**Problems found:**
- B1. Titles/sources can contain `|`, which breaks GitHub markdown tables. → **Fix:**
  `.replace("|", "\\|")` on table cells.
- B2. Multi-step fixes need line breaks inside a table cell; raw `\n` won't render. →
  **Fix:** join steps with `<br>` (renders in GitHub-flavored markdown).
- B3. A 51-row table with long fix strings is hard to scan. → **Fix:** keep the table
  for at-a-glance, add Per-incident detail blocks for depth. (Accepted; both present.)

## Engineer C — Reproducibility / over-engineering reviewer
**Problems found:**
- C1. Hard-coded absolute paths would make this non-portable. → **Fix:** derive repo
  root from `__file__` (parents[4]); allow `--src`/`--out-*` overrides.
- C2. Pulling in pytest as a dependency is over-engineering for 4 tests. → **Fix:**
  plain `assert` functions runnable via `python3 test_catalog.py`; pytest-compatible
  but not required.
- C3. Risk of under-testing the real corpus. → **Fix:** test #3 runs `collect()` over
  the actual YAML dir and asserts >=33 specs and structural invariants — catches
  schema drift, not just the toy fixture.
- C4 (rejected): "also emit CSV/HTML." → Rejected as scope creep; MD is the paper
  deliverable, JSON covers machine consumption. Two formats is enough.

## Final filtered spec
All A/B/C fixes above are folded into `04_spec.md` and the implementation:
file-keyed rows, conditional URL line, pipe-escaping, `<br>` fix joins, `__file__`-
relative paths, stdlib-only tests including a real-corpus parse test. C4 dropped.
