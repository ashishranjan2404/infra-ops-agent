# H5 — 10 Feedback for the next task

The highest-leverage move was treating the dashboard as a thin renderer over a **versioned
manifest schema** and pushing all derived logic (baseline lift, gate decision, reasons)
into a Python generator that reads the *real* upstream artifacts — so the HTML never
hardcodes numbers and the gate is reproducible. Two gotchas worth carrying forward:
(1) A1 and A2 use different key names for the same quantities (`p1`/`ci` vs `pass@1`/`ci95`),
so any cross-run aggregator must normalize per-source rather than assume one shape;
(2) browsers block `fetch()` over `file://`, so verify HTML data-loading by serving the
folder (`python3 -m http.server`) and, where Node is available, drive the page's real
`<script>` through a minimal DOM shim to assert render output — this catches JS errors that
a static HTMLParser check misses. For credibility, always include the *losing* conditions
(baselines + ablations) in any results manifest so a gate/threshold view is demonstrably
discriminative rather than a cherry-picked winners list.
