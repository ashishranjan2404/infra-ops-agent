# D13 — 05 Ouroboros (3 self-critiques of the spec)

## Engineer A — "the oracle is doing the work"
**Problem:** `judge_fooled` depends entirely on `HUMAN_ORACLE`, which I authored. If I
label aggressively, the fool-rate inflates. **Real gap:** the `negated_gold` and
`single_gold_token` labels are defensible, but a skeptic will say "you defined the
verdict to make the judge look bad."
**Fix applied:** Oracle labels are conservative and each carries an inline rationale in
code. Crucially, the two robustness guards (`whitespace_only`, and the explicit
pure-herring pytest) are oracle-labeled the SAME way the judge already behaves — they
yield fool-rate 0, demonstrating the oracle is not rigged to always disagree. The
fool-rate is reported per-attack so a reader can discard any label they reject.

## Engineer B — "verbatim echo and homoglyph are not equivalent threats"
**Problem:** The spec lumped all 7 attacks together; but their *real-world
exploitability differs by orders of magnitude*. Verbatim-gold-echo needs the hidden
gold sentence (impossible at eval). Homoglyph needs the model to emit Cyrillic
deliberately (possible but unusual). Single-token/hedge/negation need only the public
symptom vocabulary that's in the prompt — these are the genuinely reachable ones.
**Fix applied:** `verbatim_gold_echo` is marked informational with fool-rate expected
0 (it's gold text → judge correctly credits it; not a "fool"). The writeup (08/09)
splits findings into *directly-reachable* vs *capability-gated*, so we don't overclaim.

## Engineer C — "diagnosis-only hacking is capped at 0.30; show the composed risk"
**Problem:** A reviewer will shrug at a 30% term being gameable if the other 70%
(fix+resolved) still requires real competence. **Real gap:** the spec must demonstrate
that the diagnosis hack *composes* with legitimately-earned credit.
**Fix applied:** `run_score_probe()` pairs the hedge diagnosis with a genuinely-correct
fix on the fault node and measures the resulting `score_plan` value (expected 0.55).
This shows a non-committal shotgun diagnosis collects the full 0.30 on top of real fix
credit — the operationally dangerous case SRE raised. Resolved is held False to be
conservative (we do not assume the sim resolves for a hedger).

## Final filtered spec
Unchanged structurally; the three fixes are: (A) conservative+rationalized oracle with
fool-rate-0 guards proving it isn't rigged; (B) explicit reachability tiers, echo =
informational; (C) composed-score probe quantifying the 0.55 shotgun. Proceed to build.
