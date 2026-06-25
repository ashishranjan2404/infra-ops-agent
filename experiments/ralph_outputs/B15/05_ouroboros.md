# B15 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — "the brittle-parser hunter"
**Problems found:**
- A1 JSON uses key `pass@1` and `ci95`; A2 may use `p1`/`ci` from a summarizer, or `pass@1`.
  If `load_our` hard-codes one, it silently drops a model. **Fix:** try both key spellings via a
  helper `_get(d, "pass@1", "p1")` and `_get(d, "ci95", "ci")`.
- A2's `by_condition[cond]` might not carry per-family splits (it's a 30-incident ablation).
  If the script assumes `simple/cascade/novel` exist for A2, it KeyErrors. **Fix:** per-family is
  optional; only A1 must have families; A2 used for overall pass@1 only.
- Path defaults are relative to CWD; the Ralph runner may invoke from repo root. **Fix:** resolve
  paths relative to the script file (`Path(__file__).parent`) so it runs from anywhere.

## Engineer B — "the methodology skeptic"
**Problems found:**
- The headline table risks implying rex 0.90 > SREGym 0.61. **Fix:** add an explicit
  `attempt_regime` column ("multi-attempt+oracle" vs "single-run") and a bold caption that REx
  has NO SREGym counterpart. Sort so single-run-ish rows sit next to SREGym's single-attempt rows.
- "SREGym E2E band min–max" could be read as a CI. **Fix:** label it "range across agents (no
  noise)", not a confidence interval. SREGym gives no per-task CI to us.
- The family↔partition analogy could be mistaken for a validated mapping. **Fix:** prefix that
  table's title with "LOOSE ANALOGY — not a validated mapping" and repeat in caveats.
- We claim our reward is "E2E-ish" — but is it? Check rex/scoring.py semantics. The reward bundles
  SLO-restored + root-cause-cleared + no-collateral, which genuinely spans diagnose+mitigate, so
  "E2E-ish" is fair; but we cannot split it. Keep the caveat that diagnosis-only is unavailable.

## Engineer C — "the over/under-engineering auditor"
**Problems found:**
- **Under-engineered:** no `--selftest`. A table generator that silently mis-reads JSON is worse
  than none. **Fix:** add `--selftest` with the 4 spec asserts; run it in 07.
- **Over-engineered risk:** I was tempted to auto-scrape SREGym live at run time. Rejected —
  numbers are frozen with citations; live scraping adds a network dependency and reproducibility
  risk. Keep the checked-in JSON.
- Storing partition_breakdown for all 3 agents is more than the table needs (we display one
  representative). Keep the data (cheap, auditable) but only render Claude Code no-noise to avoid
  a 12-column wall.

## Final filtered spec (deltas applied)
1. `load_our` uses tolerant key lookup (`pass@1|p1`, `ci95|ci`); per-family optional (A1 only).
2. Paths resolved relative to `__file__`; CLI overrides still honored.
3. Headline table gains an `attempt_regime` column + bold "no SREGym counterpart" caption on REx;
   SREGym column labeled "range across agents (no noise)".
4. Family-analogy table title carries "LOOSE ANALOGY"; renders one representative SREGym agent.
5. `--selftest` added with 4 asserts; non-zero exit on failure.
6. SREGym numbers stay frozen + cited (no live scrape).
