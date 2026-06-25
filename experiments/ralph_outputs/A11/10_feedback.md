# A11 — 10 Feedback for the next task

The biggest practical lesson is parallel-safety: numeric file prefixes
(`80-`, `81-`...) are a shared namespace and WILL race with other Ralph workers —
I hit a live collision where another worker claimed 80-89 mid-run. Use a
task-namespaced prefix (e.g. `a11-pair-*`, `a11_pairs_manifest.json`) for any new
shared-dir artifact, and add a refuse-if-exists guard so you can never clobber.
On the substance: defining "same root cause" as `failure_class + canonical fix
tool` is clean and directly matches what the deterministic judge scores, but it
conflates "same fix" with "same reasoning path" — the next task building transfer
evals should (a) add difficulty-direction-flipped pairs to decorrelate transfer
from difficulty, and (b) actually run the canonical fix through `sim/engine.py` /
`rex/eval_pass_at_k.py` to confirm `fix_resolves` empirically rather than just
asserting it in YAML.
