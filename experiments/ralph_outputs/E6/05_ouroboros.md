# E6 — 05 Ouroboros (self-critique as 3 engineers)

## Engineer A — "the partition is leaky"
**Problem found:** The spec claims a strict partition, but `remediation` keys overlap
neither variant fully accounts for if a record's remediation has a key in *neither* list
(e.g. a future `notes` field). Silent data loss.
**Also:** `transform_state_only` strips `optimal_trajectory` from `answer` but leaves the
rest of `answer` (including `model_response`, which is a *written diagnosis* = arguably an
action/output). Is the diagnosis a state or an action? Ambiguous.
**Verdict:** Need to (a) accept that remediation keys outside both lists are intentionally
dropped (document it), (b) decide `model_response` stays in both — it's the *label*, not a
channel being ablated. The ablation is over the *trajectory supervision*, the diagnosis
label is the target, so it should remain in all variants. Spec updated to say so.

## Engineer B — "untested edges and degenerate variants"
**Problem found:** No test for a record with ZERO assistant steps or ZERO tool steps
(a degenerate trajectory). state_only/action_only would produce empty trajectories
silently — is that valid training data or garbage? Also no test that the *real* corpus
doesn't crash (the fixture is hand-made and may not match real edge cases).
**Verdict:** (a) Empty trajectory after ablation is *legal* (a record can be all-action or
all-state); the harness `mean_steps` will reflect it, downstream filtering is the trainer's
job — documented. (b) ADD a real-corpus smoke run in 07 (run on all 319 records). This is a
genuine gap; closing it by validating on real data, not just the fixture.

## Engineer C — "over-claiming and the blocker framing"
**Problem found:** The harness prints `records_with_state_transition` etc. A careless reader
could mistake these structural counts for *results*. Risk of looking like fabricated metrics
— exactly what the AAAI reviewer warned about.
**Also:** `run_ablation_e6.py`'s docstring buries the blocker. It must be impossible to read
the report without seeing "these are data facts, not model metrics."
**Verdict:** (a) Keep stat names explicitly structural (counts/steps), never "accuracy"/
"pass@1". (b) The report carries a top-level `blocker` string. (c) 08/09 state plainly: zero
model metrics produced, by design. Accepted.

## Final filtered spec deltas
1. Remediation keys outside both lists are intentionally dropped (acknowledged data loss,
   none exist in current schema).
2. `answer.model_response` (the diagnosis label) is retained in all variants — it is the
   training target, not an ablated channel; only the *demonstrated action sequence*
   (`optimal_trajectory`, `required_queries`) is stripped from state_only.
3. Empty post-ablation trajectories are legal; downstream filtering is out of scope.
4. Validate on the full 319-record real corpus, not just the fixture (done in 07).
5. Report stats are structural only; `blocker` is a top-level field. No metric-shaped output.
