# E6 — 10 Feedback for the next task

The whole Fireball/cross-domain family (E2–E10) shares one hard blocker: the real FIREBALL
D&D trajectory corpus and a fireball-trained model slug are simply not in this repo, so any
task whose *deliverable is a number* will end blocked. The productive move — proven here — is
to scope your owned deliverable to the piece that does NOT need the missing data: a tested,
deterministic transform/harness validated on the in-repo `opensre-traj/out/trajectories.jsonl`
(319 records, identical FIREBALL `state_before→fix→state_after` schema), which makes a clean
stand-in for *format/plumbing* validation even though it can't substitute for the cross-domain
experiment itself. Keep transforms pure (deep-copy, no mutation), assert a falsifiable
structural invariant (here: state_only + action_only step counts partition full exactly), and
put the "this is data, not metrics" disclaimer as a top-level `blocker` field so nothing looks
like fabricated accuracy. Next worker: reuse `E6/artifacts/fireball_ablate.py` as the variant
generator and wire its output into the existing `rex.eval_pass_at_k` + `rex.scoring` path the
moment real data lands — the only missing input is the corpus + slug, everything downstream is
already built.
