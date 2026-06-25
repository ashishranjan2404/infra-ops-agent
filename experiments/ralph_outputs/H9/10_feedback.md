# H9 — 10 Feedback for the next task

A "leaderboard" task is 20% layout and 80% data discipline. The single highest-leverage move was
treating the page as a *verifiable* artifact: split data (`leaderboard.json`) from render
(`leaderboard.html`) and write a verifier that (a) cross-checks every headline number against the
literal source-task JSONs and (b) actually serves the dir over HTTP to prove the page loads the
JSON — that turns "renders from JSON" and "real numbers" from claims into passing tests. The
recurring honesty trap across these tasks is selective/category-error reporting: mixing models and
incident families in one ranked table quietly implies an apples-to-apples ranking that isn't there,
and silently dropping a blocked arm (E3's Fireball) reads as selective reporting — solve both with a
family tag/filter and a separate unranked "blocked" panel rather than a fake `0.0` row. Next time,
go one step further than I did and *generate* the leaderboard JSON from the source artifacts with a
small build script (the verifier only catches drift after the fact; a generator prevents it).
