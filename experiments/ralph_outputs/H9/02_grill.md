# H9 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **SML** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial takes
- **SML:** A leaderboard is a presentation layer, not science. The only thing that makes it
  credible is that every cell is traceable to a real run. Each row must carry its `source`
  task id and episode count so a reader can audit it. pass@1 with a CI is the right headline.
- **PSRE:** Mixing models (glm-5p2, deepseek-v4-pro, qwen3-8b) AND families (42 vs 30 vs 14)
  in one ranked table is operationally misleading — it implies a single apples-to-apples
  ranking where there isn't one. People will screenshot row 1 and quote "0.90" with no context.
- **REV:** If this ships as a "leaderboard" it must not fabricate. The Fireball arm from E3 was
  blocked — if it silently disappears, that's selective reporting. It needs to be visible as
  "not evaluated."
- **RLE:** Don't inline the data into the HTML — the task explicitly wants a JSON-driven page.
  And prove it loads the JSON, otherwise "renders from JSON" is an unverified claim. `file://`
  fetch will fail in Chrome; that bites everyone who double-clicks the file.
- **DVO:** Zero external dependencies. No CDN React, no Tailwind from a URL. It must render
  offline from a plain `python3 -m http.server`. One HTML file, one JSON file, done.

## Round 2 — react to another persona (genuine disagreement)
- **PSRE → SML:** SML says "pass@1 + CI is the headline and we're done." I disagree — a CI
  column alone doesn't fix the category error of ranking a 42-incident glm run *above* a
  14-incident qwen run as if #1 beats #8. The fix isn't statistical, it's UX: a **family
  filter** so a reader compares within a family, plus a column making `family` impossible to miss.
- **RLE → REV:** REV wants the blocked Fireball arm shown in the table itself. I disagree —
  putting a row with empty pass@k *in the ranked table* invites someone to read it as 0.0 and
  rank it last, which is a different lie. Better: a separate "Blocked / not evaluated" panel
  below the board. Honest, but not rankable.
- **SML → DVO:** DVO's "zero deps, one file" purism is fine until you want a CI bar or sorting.
  I push back lightly: vanilla JS can do bars and sort with ~80 lines — no framework needed —
  so DVO and I actually converge, but only if we accept hand-rolled JS instead of "just a table."
- **DVO → RLE:** RLE is right that file:// breaks fetch, but I object to "just tell people to
  use a server" as the whole answer — a public page that shows a blank screen on double-click
  looks broken. We must catch the fetch error and render an actionable message in-page.
- **REV → PSRE:** PSRE wants to de-emphasize the cross-model ranking. I partly disagree: the
  single most important scientific claim here *is* cross-condition (REx vs zero_shot within a
  model), and that IS apples-to-apples (same model, same 42 set). So keep rank, but rank should
  visibly default by pass@1 while the family tag + filter prevent the cross-family misread.

## Round 3 — synthesis (what we agreed to do)
1. **Data/render split, JSON-driven** (RLE/DVO): one `leaderboard.json`, one `leaderboard.html`
   that fetches it. Prove the load with an HTTP verifier (RLE).
2. **Provenance on every row** (SML): `source` task id + episode `n` + per-row CI shown.
3. **Family is first-class** (PSRE): a `family` tag column + a family filter dropdown so
   within-family comparison is one click; cross-condition same-model rows (the real claim)
   stay adjacent and highlighted.
4. **Blocked arm is visible but unranked** (REV/RLE): Fireball shown in a separate panel, not
   as a fake table row.
5. **Offline, zero-dep, graceful file:// error** (DVO): no CDN; catch fetch failure and tell
   the user to serve over HTTP.
6. **pass@1 + CI is headline; pass@5 flagged as low-seed upper bound** (SML, inherited A1 caveat).
