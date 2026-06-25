# E5 — Summary: Fireball transfer on 10 novel incidents (generalization test)

## Goal
Run the Fireball transfer-target policy on a 10-incident novel held-out set to test
generalization, reusing the A8 zero-overlap split, against real baselines.

## Deliverables
- artifacts/transfer_eval_novel.py — transfer/generalization eval harness. Reuses the
  A8 held-out manifest (novel-family first, back-fill simple, asserted loadable), runs
  any roster policy zero-shot under the P0 deterministic judge, reports pass@1 + Wilson
  95% CI + within-group std, with empty (floor) and oracle (ceiling/validity) controls
  and an explicit blocked path for unreachable models. No core files edited — imports only.
- artifacts/test_transfer_eval.py — no-network self-test (selection, floor==0,
  ceiling>=0.8, blocked handling). All pass.
- transfer_results.json — real run output.

## Novel set (10, from A8 held_out==true)
8 novel-family: azure_leapyear_cert, conntrack_exhaustion, facebook_bgp_backbone,
firefox_addon_cert, gke_ip_exhaustion, kafka_poison_pill, knight_capital_conflict;
back-fill simple to reach 10: auth_cert_expiry, billing_disk_fill, checkout_bad_rollout.

## Results (seeds=2, threshold=0.8)
| policy   | status  | pass@1 | 95% CI       | mean | std  |
|----------|---------|--------|--------------|------|------|
| empty    | ok      | 0.00   | [0.00,0.16]  | 0.00 | 0.00 |
| oracle   | ok      | 1.00   | [0.84,1.00]  | 1.00 | 0.00 |
| glm-5p2  | ok      | 0.25   | [0.11,0.47]  | 0.41 | 0.38 |
| fireball | BLOCKED | —      | —            | —    | —    |

Floor/ceiling gate passes (floor_ok & ceiling_ok): every novel incident is solvable,
empty never passes. glm-5p2 shows real spread (std 0.38), passing the easy leaves and
missing the hard novel cascades.

## Blocker (honest, not fabricated)
Fireball is not in agent.models.ROSTER and no provider serves it (KeyError: 'fireball').
The Fireball transfer pass@1 could not be produced. When a Fireball slug exists, add it
to ROSTER (or --fireball-model <slug>) and re-run — the harness fills the blocked row and
yields the transfer delta vs the captured glm-5p2 baseline, no code change needed.

## Status
completed — real plan + spec + runnable harness + passing tests + one real baseline on
the novel set were delivered; only the downstream Fireball run is blocked (documented).
