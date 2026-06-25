# H9 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer A — Frontend/accessibility
**Problems found:**
- A1: pass@5=1.00 rows next to pass@1=0.90 invite the reader to quote the inflated number.
  The A1 caveat (pass@5 degenerate at seeds=3) must be in `metric_notes`, surfaced in the
  header — DONE (header `meta` prints `metric_notes`).
- A2: clicking a `th` to sort by a string column had no tie-break and could feel random.
  Acceptable — `localeCompare` is stable enough for this size; not fixing (low value).
- A3: color-only highlight is an accessibility smell. Mitigated: highlight also changes the
  rank color and the bar gradient, and the row keeps full text — not purely color-coded.

## Engineer B — Data integrity
**Problems found:**
- B1: E3 has no pass@5 (seeds=2). If the renderer assumed a number it would print "NaN%".
  Fixed: `fmtPct(null)` returns "—"; `pass@5: null` is explicit in the JSON. Verified.
- B2: Ranking mixes families/models — a real category-error risk (PSRE). Mitigated by the
  `family` tag + filter (not eliminated; documented in 09 as a known limitation).
- B3: Could the JSON drift from the source tasks over time? Yes. That's exactly why
  `verify_leaderboard.py` cross-checks 5 anchor numbers against the literal A1/A2/E3 values —
  drift breaks the test. DONE.

## Engineer C — Build/deploy & "does it actually load"
**Problems found:**
- C1: `file://` fetch fails silently in the original sketch → blank page. Fixed: try/catch
  renders an actionable HTTP-server message.
- C2: "renders from JSON" was asserted, not proven. Fixed: the verifier spins up a real
  `socketserver` and GETs both files, asserting 200 + parse + matching entry count. This is the
  load-bearing check for the task's "verify it loads the JSON" requirement.
- C3: Port 8754 could collide on a busy box. Low risk for a one-shot verify; if it ever
  collides, `TCPServer` raises and the run fails loudly (acceptable, not silent).

## Final filtered spec changes
- Keep `pass@5: null` + "—" rendering (B1).
- Keep metric caveat in header (A1).
- Keep HTTP verifier as the canonical "loads JSON" proof (C2).
- Accept (document, don't fix): cross-family ranking is mitigated not removed (B2); port
  collision is loud-fail (C3); string-sort tie-break is good-enough (A2).
