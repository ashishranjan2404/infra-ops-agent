# H6 — 02 Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take

**SMR:** A CI gate that only proves YAML loads is weak signal for an *RL environment*. The
thing that matters is that the injected fault actually bites and the canonical fix resolves it —
otherwise you're shipping tasks with no reward signal. Acceptance-only feels like box-ticking.

**PSRE:** Disagree on priority. In an SRE incident corpus, the most common breakage isn't
"reward is wrong", it's "someone hand-edited a YAML and now it `KeyError`s on load at 3am in
the eval pipeline". A fast, deterministic acceptance gate that fails the build is exactly the
hygiene you want. Exit codes must be unambiguous.

**AAAI:** For a paper, the claim is "we validate every scenario." A reviewer will ask: validate
*what property*? You must define the contract precisely — schema conformance + engine acceptance
is a defensible, falsifiable claim. But don't overclaim it as "scenarios are correct."

**RLE:** I care that the action space is exercised. Loading isn't enough; you should actually
push every `canonical_fix` step through `apply_action` so a typo'd tool name or bad target shape
is caught. Otherwise the gate is green and the env still explodes at rollout time.

**DOL:** Whatever you build, it has to be one command, no flags required, and return a real exit
code. A `.sh` wrapper and a JSON artifact for the CI logs. If it needs a venv or env vars, it
won't run in CI.

## Round 2 — react to another persona by name (genuine disagreement)

**PSRE → SMR:** You're conflating two gates. "Does the fix resolve?" (your concern) is a
*semantic* check that's inherently flakier and already owned by A16. Bolting it into the *CI
acceptance gate* means every reward-tuning experiment turns CI red — you'd be coupling build
health to research-in-progress. Keep them separate. H6 is the load-bearing wall; A16 is the
paint.

**SMR → PSRE:** Fair, but then H6 must be honest about its weakness in the writeup, not market
itself as "scenarios validated." I'll concede the separation if the docs explicitly say H6 is
acceptance-only and name A16 as the semantic layer.

**AAAI → RLE:** I push back slightly — exercising `apply_action` is good, but be careful: if the
fix doesn't resolve, `apply_action` still returns normally (it just doesn't clear the fault).
So "apply runs without raising" is a *much* weaker claim than "fix works". State that boundary
or a reviewer calls it a false sense of security.

**RLE → AAAI:** Agreed, and that's actually the point — H6's `apply_fix` stage catches *crashes*
(bad tool/target shapes), not *ineffective fixes*. Different failure mode. I'll make the stage
semantics explicit so nobody reads green-H6 as "fix verified."

**DOL → PSRE:** One more: exit code 2 vs 1 matters. If the glob matches nothing because someone
moved the dir, that must NOT look like "all pass" (exit 0) — that's a silent-success trap that's
bitten every CI I've run. Make "no scenarios found" a hard exit 2.

## Round 3 — synthesis

Consensus:
1. **Scope H6 as acceptance-only** (load + schema + engine-runs), explicitly *not* fix-resolves
   (that's A16). Document the boundary so green-H6 is not misread (SMR, AAAI, RLE).
2. **Exercise the action space** by pushing canonical_fix through `apply_action`, framed as a
   crash check, not an efficacy check (RLE, AAAI).
3. **Hard, distinct exit codes**: 0 pass, 1 scenario failure, 2 harness/no-match/import error —
   no-match must never read as success (DOL, PSRE).
4. **One-command CI ergonomics**: `.sh` wrapper, JSON artifact, stdlib + pyyaml only, no env
   vars (DOL).
5. **Per-stage failure categorization** so a red build points at the exact broken stage (PSRE).
