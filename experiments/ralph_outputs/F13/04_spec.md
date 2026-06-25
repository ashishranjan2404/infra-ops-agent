# 04 — Spec

## Deliverables
1. `artifacts/poster.md` — markdown source of the poster (source of truth, citeable).
2. `artifacts/poster.html` — self-contained A0 portrait poster, print-styled.
3. `artifacts/validate_poster.py` — validator (run in step 07).

## poster.md format
Plain CommonMark. Top-level `# <title>`, then `## <SECTION>` for each of the required
sections plus extras. Every quantitative claim followed by an inline source tag
`[src: <file>]`. Required sections (exact substrings, case-insensitive): `Motivation`,
`Method`, `Benchmark`, `Results`, `Takeaways`.

## poster.html structure
- `<!DOCTYPE html>`, `<html lang="en">`, single `<style>` block (inlined, no external refs).
- Layout: `.poster` container fixed to A0 portrait (841mm × 1189mm) on screen; CSS grid
  header + 3-column body.
- CSS contract:
  - `@page { size: A0 portrait; margin: 0; }`
  - `@media print { .poster { box-shadow:none; } body { margin:0; } }`
  - System font stack only: `-apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
  - Section cards `.card` with header bars; hero numbers `.bignum`.
- Sections (each a `<section class="card">` with an `<h2>`): Motivation, The Cascade,
  Environment (hero), Method / Reward, Two-Tier Contract, Benchmark, Results (two co-equal
  sub-panels: Frontier sweep + Ablation caveat), Takeaways, Reproduce.

## Numbers to display (all grounded — source in brackets)
- Reward: `0.30·diagnosis + 0.25·correct_fix + 0.45·resolved − 0.60·trap`, clamp 0..1.
  [ARCHITECTURE.md / rex/scoring.py]
- Frontier sweep (5 frozen models, same 5 incidents): baselines 0.63–0.81 → REx 0.86 all;
  haiku +0.23, opus +0.05; 0.86 = (4×1.0+0.30)/5 = solve 4 + correctly escalate 1.
  [ARCHITECTURE.md]
- Honest one-shot band: haiku 0.27 vs opus 0.50 mean; 20–50% reward band w/ real variance.
  [docs/headline_insights.md]
- Verifier generalization: trained on 7 incidents, gates 3 held-out at 0.90 acc vs 0.95
  hand-written; compresses 14→3 rules, zero synthesis-quality misses. [headline_insights.md]
- Ablation caveat: with root-cause hint stripped, REx 0.25 ≈ zero-shot 0.24; best-of-N 0.24;
  outcome-only retry 0.23 → ~0 gain. [docs/headline_insights.md / rex/runs/ablation.json]
- Within-group reward spread 0.0 / 0.15 / 1.0. [ARCHITECTURE.md]
- Scenario catalog: 9 CIDG + reconstructed real outages (AWS DynamoDB DNS, Cloudflare WAF,
  CrowdStrike CF291, Railway/GCP, Azure DDoS). [ARCHITECTURE.md]

## validate_poster.py contract
- `check_markdown(path)`: returns list of missing required sections.
- `check_html(path)`: parses with `html.parser` (HTMLParser subclass) tracking tag stack;
  returns list of well-formedness errors (unclosed/mismatched non-void tags); also asserts
  presence of `@page`, `@media print`, `size: A0`, and each required section heading text.
- `check_no_placeholder(text)`: flags `lorem`, `TODO`, `FIXME`, `xxxx`.
- `main()`: runs all, prints a report, exits 0 iff zero errors. Self-contained, stdlib only.

## Test cases
- T1: poster.md contains all 5 required section substrings → 0 missing.
- T2: poster.html is well-formed (tag stack empties) → 0 errors.
- T3: poster.html contains `@page`, `@media print`, `size: A0` → present.
- T4: no placeholder tokens in either file → 0 flags.
- T5: every `[src: ...]` in poster.md references a path that exists in repo (spot subset).
