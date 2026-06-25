# D8 — 05 Ouroboros (self-critique as 3 engineers in sequence)

## Engineer 1 — "Data Integrity" reviewer
**Problems found:**
- The reward formula gives 0.8 to a *miss* (no state change) — but a miss is a
  perfectly valid, informative transition for a dynamics learner. Is down-weighting
  no-change turns even correct? It biases the SFT set toward "something happened",
  which could teach the model that actions always change state — wrong for SRE
  (a probe that returns "nothing wrong" is a real, important transition).
- `before_state != after_state` does a deep equality on raw dicts/lists; key
  ordering or float vs int hp could make identical states compare unequal.
- Malformed lines are dropped silently to stderr; in a real ingest you'd want a
  count surfaced in the returned stats, not just a warning.

**Filtered decisions:** Keep the no-change down-weight but make it *mild* (0.8 not
0.0) and document it as a *quality* signal, not a correctness gate — a miss still
trains. The deep-equality concern is real but acceptable for the fixture; flagged
in 09 as a hardening item for real data (normalize states before compare). Silent
malformed-drop is acceptable for a scaffold; noted.

## Engineer 2 — "API/Contract" reviewer
**Problems found:**
- `commands` could be a single string in the real dump, not a list. `_join`
  handles both — good — but the skip check `if not command` relies on `_join`
  returning "" for `[]` and `None`. Verified it does.
- `convert_file` writes output even when 0 examples are produced (empty file).
  For a real run that silently yields an empty training set, which a guard should
  catch. The *config* carries `min_examples_for_real_run`, but the adapter itself
  doesn't enforce it. Contract gap between adapter and config.
- No schema-version field in output; if the format evolves, downstream can't tell.

**Filtered decisions:** The min-examples guard lives at the *training* layer
(config), not the adapter — the adapter is intentionally a pure transform. This
is a deliberate separation, documented. Empty-output is therefore expected and
fine for the transform. Schema-version: out of scope for D8, noted as nice-to-have.

## Engineer 3 — "Scope/Over-engineering" reviewer
**Problems found:**
- Is the system prompt necessary? It bakes an interpretation ("this mirrors
  diagnosing...") into every example. If wrong, it's a systematic bias. But it's
  also the entire transfer thesis made explicit — defensible, keep, but it IS an
  assumption the eval must validate.
- The fixture has 7 records — enough to hit every branch but trivially small.
  That's the point (it's a fixture), but a reviewer might mistake it for the
  training data. Must be unmistakably labeled synthetic. (It is: `syn-combat-*`
  ids + blocker docs.)
- `_fmt_state` invents a compact rendering; the real FIREBALL state is much
  richer (positions, conditions, spell slots). We're discarding signal.

**Filtered decisions:** Keep the system prompt but explicitly flag it as a tested
assumption in 09. Fixture smallness is intentional and labeled. Discarding rich
state is acceptable for v1 — the adapter is extensible (`_fmt_state` is one
function); richer rendering is a documented follow-up, not a v1 blocker.

## Final filtered spec deltas
- Reward: keep mild no-change down-weight, reframed as quality not correctness.
- Adapter stays a pure transform; min-examples guard stays in config layer.
- State-equality normalization + richer `_fmt_state` + schema-version = recorded
  follow-ups in 09, not v1 scope.
- Synthetic fixture must remain unmistakably labeled (it is).
