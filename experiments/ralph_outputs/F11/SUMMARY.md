# F11 — SUMMARY

**Task:** Create the artifact-evaluation appendix for the AAAI artifact track — how to obtain,
build, and run the SRE-Degrees benchmark + REx eval, expected outputs, hardware, and a
badge-claim mapping. Grounded in the real repo. No shared-core edits.

## Delivered (experiments/ralph_outputs/F11/artifacts/)
- **APPENDIX.md** — full AAAI/ACM artifact appendix (sections A.1–A.9): abstract, check-list
  meta-info, access/HW/SW/data, install, two-tier experiment workflow (offline Functional /
  online Reproduced), expected results + reproduction tolerance, customization, threats, badge map.
  Commands grounded in rex/eval_pass_at_k.py, rex/scoring.py, scenarios_by_family(), floor_check,
  experiments/compute_pass_at_k.py. No invented numbers.
- **badge_claim_map.json** — machine-readable Available/Functional/Reproduced -> claim -> command
  -> evidence -> expected mapping.
- **smoke_ae.sh** — offline, credential-free Functional smoke (registry load + full-registry floor
  check + deterministic-judge tests). Runs RC=0 here.
- **test_badge_map.py** — pytest validating the badge map schema + that named files/flags are real.

## Verification (real output in 07)
- smoke_ae.sh -> exit 0; families {simple:12, cascade:20, novel:10}; floor_ok=True
  (trap_max=0.1 < 0.8); judge tests 12 passed.
- test_badge_map.py -> 6 passed.
- APPENDIX.md -> 9 sections present, code fences balanced.
- Sim determinism probe -> identical plan => identical reward.
- No shared-core files modified (verified by mtimes vs session start).

## Blocker (documented, not faked)
Tier B (the full pass@k sweep that earns Results Reproduced) needs a live LLM gateway key + real
API spend; not run. The appendix ships the exact, verified reproduction command + comparison keys +
CI-overlap tolerance instead. Deliverable is complete; only the paid downstream run is deferred.

**Status: completed.**
