# F7 — Summary

**Task.** Write a rebuttal-anticipation doc: top 8–12 likely reviewer attacks on SRE-Degrees,
each in strongest form + best honest response, grounded in real weaknesses (synthetic data,
small N, flat RFT, reward-hacking, single domain).

**Delivered (all under `experiments/ralph_outputs/F7/`):**
- `artifacts/rebuttal_anticipation.md` — 10 attacks (A1–A10), each = Steelman + Honest response +
  Probability + Depth + Closing evidence; two top-line callouts (highest-probability rejection =
  small N; highest-depth = construct validity); concession ledger; "what would actually sink the
  paper."
- `artifacts/attacks.json` — machine-readable index; themes cover all 5 mandated weaknesses.
- `artifacts/validate_attacks.py` — stdlib validator (schema + theme coverage + doc structure +
  substance gate + A6 arithmetic check). Exits 0.
- 10 ralph step files (01–10) + this summary + result.json.

**The 10 attacks.** A1 small-N/no-CIs · A2 construct validity (Fatal-if-true) · A3 reconstruction
answer-leakage · A4 flat RFT (0.522→0.491) · A5 reward-hacking · A6 0.86 fixed point · A7 single
domain · A8 circular LLM judge · A9 unpinned gateway models · A10 REx = known search.

**Tests.** Validator PASS (exit 0) after fixing 2 self-found bugs (label-regex tolerance,
body-extraction stop). JSON parses. Negative control confirms theme check bites.

**Grounding.** Real numbers pulled from ARCHITECTURE.md, `rex/scoring.py`, `opensre-traj/`, and
the spec corpus (51 CIDG YAML + 19 reconstructed post-mortems).

**Honest limits.** It's anticipation, not proof — every "closing evidence" is a future
experiment, not a run result. Validator checks form/substance-length, not argument quality.

**Core files touched:** none (only F7/ created).

**Status:** completed.
