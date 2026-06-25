# 02 — Grill (5 personas, 3 rounds)

Personas: Senior ML Researcher (MLR), Principal SRE (SRE), AAAI Reviewer (REV),
RL Engineer (RLE), DevOps Lead (DVO).

## Round 1 — initial takes
- **MLR:** A taxonomy is only useful if it predicts reward behaviour. Tie each
  category to the `0.60` penalty in `score_plan` or it's just folksonomy.
- **SRE:** The four families map cleanly to real on-call anti-patterns: scale it,
  bounce it, roll it back, fail it over. That's exactly the "looks-busy" quadrant.
  Good real-world face validity.
- **REV:** Where's the ground truth? If you classify on *tool name* you're doing a
  lookup, not a taxonomy. Justify why tool is the right axis vs. failure_class.
- **RLE:** If 94% of scenarios share one trap verb, the trap-avoidance reward term
  is degenerate — a model learns "don't scale" and gets full credit. The taxonomy
  must surface that, not hide it.
- **DVO:** failover is the scariest trap in production (spreads blast radius). If the
  corpus has zero failover traps, that's the headline, not a footnote.

## Round 2 — react to another persona (genuine disagreement)
- **REV → SRE:** I disagree that face validity is enough. Your four families are
  plausible but *unfalsifiable* as written. Tool-name lookup means any future tool
  silently becomes "unclassified." Where's the catch-all? Without it the taxonomy
  lies by omission.
- **RLE → MLR:** You say tie it to the penalty — but the penalty is *flat* `0.60`
  regardless of which trap. So the taxonomy adds NO reward signal today; all four
  categories are scored identically. Don't oversell "predicts reward."
- **SRE → DVO:** Pushing back — failover being absent isn't a flaw of the taxonomy,
  it's a flaw of the *taskset*. Don't blame the classifier for a gap in the data.
- **MLR → REV:** Tool *is* the right axis because `_traps_in()` literally matches on
  tool first; failure_class is the *cause*, not the *wrong action*. The taxonomy is
  about wrong actions. So tool-axis is correct, not lazy.

## Round 3 — synthesis
- Accept REV's catch-all demand → add `other-trap` so unknown tools never vanish.
- Accept RLE/MLR correction → state plainly that the penalty is flat, so the
  taxonomy is *descriptive/diagnostic*, not a new reward signal (yet). Don't oversell.
- Accept DVO → make zero failover coverage a first-class finding in the doc.
- Reject SRE's "don't blame the classifier" only partially: the classifier isn't to
  blame, but the *report* must own the taskset gap, since that's the actionable
  insight.
- Keep tool-axis (MLR/grounding) but cross-reference failure_class in the doc table
  so the cause↔wrong-action contrast is visible.
