# J7 — 03 Improved Plan

## What changed after the grill

1. **Metric renamed and scoped (AAAI, PSRE — accepted).** The runner reports
   `action_select_accuracy`, explicitly distinct from the bench's live
   `reward`/recovery chain. The runner sets `cloud_executed=false` at the top level and
   `cloud_applied=false` on every row so a dry-run can never be mistaken for a live pass.

2. **Interpretability baselines added (AAAI, SMR — accepted).** We report the chance
   rate (1/15 ≈ 0.067) and a deterministic lexical baseline policy, so the LLM's lift is
   visible and the run is reproducible with no API key.

3. **Blocker-check-first ordering (DVO — accepted).** Before building, verify the temp
   GCP account / cluster. We never fall back to a personal billed account.

4. **Menu-leakage caveat documented (SMR/AAAI — accepted as a caveat, not a redesign).**
   The action space is the union of the 15 gold fixes (a defined discrete action space,
   per SMR's Atari analogy). We do NOT claim this measures execution success, and we note
   the service-name overlap inflates the lexical baseline. The honest free-form-command
   version is named as future work gated on a live cluster.

5. **Chosen command recorded, never executed (DVO, PSRE — accepted).** Each row carries
   `chosen_action_cmd` plus `cloud_blocked_reason`. Applying it is the explicit blocked
   downstream step.

## Rejected / deferred

- **PSRE: "only the live recovery chain is a valid reward."** Rejected *for this task* as a
  blocker (no cluster exists). Accepted *as a label discipline*: we keep action-selection
  and recovery as separate, non-conflated metrics. The live recovery scoring already
  exists in `stages/07_verify.sh`; J7 doesn't duplicate it, it feeds into it (the agent's
  chosen command is what stage 06 would `eval`).

- **Full free-form command generation env.** Deferred to future work — it needs a live
  cluster to grade, which is exactly the blocker.

## Final shape (unchanged core)
`agent_bench_runner.py` with `--dry-run` (offline, $0) and `--live-agent MODEL`
(real LLM call, no cloud). Reads both registries read-only. No shared core file edited.
