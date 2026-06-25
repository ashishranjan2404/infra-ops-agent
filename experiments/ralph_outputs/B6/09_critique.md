# B6 — 09 Critique (honest)

## What a reviewer attacks
1. **Constructed rollouts, not real model traces.** The 0.4804 rate is over a synthetic
   policy (deterministically one safe + one trappy agent per scenario), so by construction the
   rate hovers near 0.5 — it demonstrates the *metric machinery*, not a real agent's safety.
   A skeptic rightly says "show me this on actual Claude-Haiku rollouts." Mitigation: the
   metric eats `rex/loop.py`'s native `failed_checks` format unchanged, so pointing it at a
   real run is a one-liner — but that real run was not available/executed here.
2. **Executed-only trap notion.** We measure traps that were *applied*. An agent that
   repeatedly lunges for the dangerous lever but is caught by the safety harness scores as
   safe. PSRE/RLE flagged this in the grill; we deliberately scoped to executed traps to stay
   grounded in the judge, but the more interesting *intent* metric (`attempted_trap_rate` over
   `blocked_actions`) is unbuilt. This is the biggest conceptual gap.
3. **Degeneracy.** Read alone, a do-nothing agent scores 1.0. We document that it must be read
   against resolved-rate, but we don't *enforce* co-reporting — a careless consumer could quote
   the safety number in isolation.
4. **Predicate-mirror duplication.** We re-implement `_traps_in` instead of importing it (for
   parallel-safety). The equality test guards against drift today, but if `_traps_in` gains a
   new clause (e.g. arg-value matching beyond `target`), the test would catch divergence only if
   its fixtures exercise the new clause — silent drift on untested branches is possible.
5. **Naive YAML fallback parser** is brittle (indent-sensitive, only `tool`/`target`). It's a
   fallback behind PyYAML and behind the failed_checks path, but it's the weakest code here.

## What's weak / missing
- No real-model rollouts; no attempted-vs-executed split; no enforced co-reporting with
  competence; no per-action variant; the two "2-trap" scenarios reveal a CIDG design ambiguity
  (fix tool == trap tool) that this metric surfaces but does not resolve.

## What's solid
- Tight grounding in the judge with a passing equality test; two independent signal paths that
  agree on real YAML-derived data; explicit UNKNOWN handling so missing data never inflates
  safety; zero shared-core edits; runs clean with and without pytest/PyYAML.
