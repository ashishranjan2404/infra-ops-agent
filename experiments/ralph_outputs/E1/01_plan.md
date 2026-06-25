# 01 — Plan (E1: Get Wenji's GRPO branch pushed to the repo)

## Objective
Unblock paper Claim 2 ("Fireball D&D-trajectory transfer improves cascade pass@1 over
SRE-only GRPO training") by getting Wenji's finished-but-unpushed GRPO branch and its
Fireball training data into the repo `git@github.com:ashishranjan2404/infra-ops-agent.git`.

## Honest framing of the task type
This is a **coordination / blocker task, not an executable code task**. The deliverable
explicitly is NOT a model run. I (this worker) **cannot push a branch that lives only on
Wenji's machine** — the code/data/checkpoint are not in this repo, not on `origin`, and
not on the HUD model registry (per `experiments/results/P7_fireball_status.md`). So the
right outcome is a *correct, evidence-grounded coordination package*, plus a runnable
verification harness Wenji can self-check against before/after pushing.

## Approach
1. **Inventory** every piece of GRPO/RFT machinery that ALREADY exists in-repo (so Wenji's
   push only needs to add what is genuinely missing, not re-add what we have).
2. **Expectation list** — derive, from the meeting notes (`ACTION_ITEMS.md`,
   `TEAM_SUMMARY.md`, `PAPER_QUESTIONS.md`, `NEXT_100_TASKS.md`) and the existing code,
   the precise set of files a "Wenji GRPO branch" must contain to be replicable.
3. **Integration checklist** — a merge/review checklist (branch hygiene, no-secrets,
   reward parity, eval entrypoint) so the push is mergeable, not a dump.
4. **Draft request message** — a ready-to-send message to Wenji with an exact `git`
   recipe and a manifest of what to include.
5. **Verification harness** — a small read-only script that, run against the repo *after*
   the push, asserts the expected artifacts are present, parseable, and that the GRPO
   reward matches the in-repo deterministic judge (reward parity). This is the real,
   runnable artifact.

## Files to create (all task-namespaced, no shared-core edits)
- `experiments/ralph_outputs/E1/artifacts/grpo_inventory.json` — machine-readable inventory.
- `experiments/ralph_outputs/E1/artifacts/wenji_branch_manifest.md` — what's expected.
- `experiments/ralph_outputs/E1/artifacts/integration_checklist.md` — merge checklist.
- `experiments/ralph_outputs/E1/artifacts/request_message_to_wenji.md` — draft message + git recipe.
- `experiments/ralph_outputs/E1/artifacts/verify_grpo_push.py` — read-only post-push verifier.
- The 10 step docs + SUMMARY.md + result.json.

## Dependencies
- Local git (read-only inspection of branches/remotes) — available.
- `python3` (3.13) for the verifier — available.
- Wenji (human) to actually push — NOT available to this worker. This is the blocker.

## Risks
- Risk: producing a vague "please push" note. Mitigation: ground every "expected" item in
  an existing in-repo counterpart and give an exact git recipe + manifest.
- Risk: the verifier hard-codes assumptions that don't match Wenji's layout. Mitigation:
  make it tolerant (checks by glob/content, prints a checklist, exits non-zero only on the
  load-bearing misses), and document expected paths.
- Risk: leaking secrets if Wenji's branch carries `.env`/keys. Mitigation: explicit
  no-secrets item in the checklist + a grep step in the verifier.

## Success criteria
- A complete, accurate inventory of in-repo GRPO code (verified against `git`/filesystem).
- A precise, justified expectation list for Wenji's branch.
- A mergeable integration checklist.
- A send-ready request message with a copy-paste git recipe.
- A verifier that runs cleanly today (reporting "branch not yet pushed — blocked") and will
  validate the push when it lands.
- The blocker documented honestly: **this worker cannot push someone else's branch.**
