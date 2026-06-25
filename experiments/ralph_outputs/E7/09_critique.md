# E7 — 09 Critique (honest)

## What's weak
1. **No real transfer numbers.** The headline scientific question — *does the
   policy transfer?* — is unanswered. We shipped a bridge, not a result. A
   reviewer can fairly say "this is engineering scaffolding, not evidence."
2. **Synthetic fixtures could be too easy.** They're hand-authored so the
   adapter always finds a clean gold. Real Jericho logs have noisy `valid_actions`
   and long observations that may break the thin field-mapping assumptions.
3. **Field-name guesses for loaders.** TextWorld/Jericho/ALFWorld field names are
   documented from memory of their APIs. The real loaders may differ (e.g.
   TextWorld's `infos["admissible_commands"]` nesting). The adapters would need a
   one-line tweak each against the actual env objects.
4. **Lexical judge mismatch.** `deterministic_judge` is stem-overlap; game gold
   ("open chest with brass key") vs agent prose may pass/fail for vocabulary
   reasons, not reasoning quality. Plan mitigates with the LLM judge but that's
   untested here.
5. **Oracle-handicap not yet ablated.** The hook exists (`meta["warnings"]`) but
   no run exercises the off-oracle condition — the metric the plan calls the
   "headline" is precisely the one not yet produced.

## What a reviewer attacks first
- "You validate that a game dict can be reshaped into your dataclass. That's a
  type-conversion test, not a transfer experiment." — **Fair.** Rebuttal: the
  task asked for a *generic adapter + unit test on a synthetic fixture + a plan*;
  the live run is explicitly blocked by the sandbox, and we did not fabricate it.
- "Game success ≠ SRE competence (irreversibility, save/restore)." — acknowledged
  as a first-class caveat in TRANSFER_PLAN.md, not hidden.

## What's missing
- A dedicated test that the off-oracle warning path fires (noted in 05, deferred
  to keep the suite focused).
- A real loader shim for at least TextWorld (needs the package; blocked).
- Statistical power analysis for how many episodes C2 vs C1 needs.

## Net honest verdict
Solid, correct, self-contained **scaffold + protocol**; the transfer claim itself
remains **unproven and blocked**. Status = completed (deliverable produced),
downstream run blocked.
