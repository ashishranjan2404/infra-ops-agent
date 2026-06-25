# J1 — 07 Test Results

## Test 1 — Harness self-test (offline, no cluster) — PASS
```
$ python3 experiments/ralph_outputs/J1/artifacts/j1_agent_runner.py --backend sim --selftest
[PASS] j1-payments-error            victim=gateway   oracle=True herring=False
[PASS] j1-payments-latency          victim=gateway   oracle=True herring=False
[PASS] j1-db-pool-stress            victim=gateway   oracle=True herring=False
[PASS] j1-checkout-egress-delay     victim=gateway   oracle=True herring=False
[PASS] j1-gateway-pod-kill          victim=gateway   oracle=True herring=False
exit=0
```
For every experiment: the gold root cause scores True AND blaming the loud victim
(red herring) scores False, and a loud victim was identified. The shared
`rex.scoring.deterministic_judge` is the grader.

## Test 2 — Per-experiment grader (offline) — PASS
```
j1-payments-error            score(gold)=True
j1-payments-latency          score(gold)=True
j1-db-pool-stress            score(gold)=True
j1-checkout-egress-delay     score(gold)=True
j1-gateway-pod-kill          score(gold)=True
```

## Test 3 — Manifest structural + RBAC-invariant — PASS
```
Namespace.metadata: OK
Job.spec: OK
ServiceAccount.metadata: OK
Role.rules: OK
RoleBinding.roleRef: OK
RoleBinding.subjects: OK
chaos delete allowed: True
pod delete NOT allowed: True
ALL OK
```
Confirms least-privilege: the runner can delete chaos CRs (heal) but cannot delete
pods/deployments.

## Test 4 — YAML multi-doc parse — PASS
```
j1_chaos_experiments.yaml: 5 docs -> ['HTTPChaos','HTTPChaos','StressChaos','NetworkChaos','PodChaos']
j1_staging_deploy.yaml:    5 docs -> ['Namespace','Job','ServiceAccount','Role','RoleBinding']
```

## Test 5 — Sim run with a baseline (wrong) and a correct agent — PASS
- `--agent-cmd 'echo "the gateway is failing"'` -> diagnoses gateway -> scored False
  on the payments-root experiments (correctly rejected as the loud victim).
- `--experiment j1-payments-error --agent-cmd 'echo "payments service returning errors"'`
  -> scored True. Demonstrates the agent contract (obs JSON on stdin -> diagnosis stdout)
  and the grader discriminating correct from victim-blaming diagnoses.

## Test 6 — LIVE cluster — **BLOCKED** (precise blocker)
Two independent blockers, both reproduced:

### (a) gcloud auth dead
```
$ gcloud config config-helper --format=json
ERROR: (gcloud.config.config-helper) There was a problem refreshing your current auth
tokens: ('invalid_grant: Account has been deleted',
{'error': 'invalid_grant', 'error_description': 'Account has been deleted'})
```
The active gcloud account `devstar4126@gcplab.me` has been deleted. The kubeconfig
(`gcp-bench/state/gke-kubeconfig.yaml`) uses the `gke-gcloud-auth-plugin` exec
credential, so EVERY `kubectl` call — even client-side `--dry-run=client` — fails at the
credential step. Other credentialed accounts (`ashishranjan2404@gmail.com`,
`ashishranjanusa2404@gmail.com`) exist but are not the cluster's account and were not
switched (no project access verified; switching could disrupt other concurrent work).

### (b) API server unreachable
```
$ curl -sk --max-time 6 https://136.114.32.127/livez
http_code=000 time=6.011s exit=28   (timeout)
```
The API server `136.114.32.127:443` does not answer even unauthenticated — consistent
with GKE master-authorized-networks restricting access to this host's IP, or the
control-plane endpoint being private. So even with valid creds, kubectl from this
workstation would not reach the cluster.

### Consequence
`kubectl apply --dry-run` (server-side and client-side via the project kubeconfig),
the live `--backend kube` harness path, and Chaos Mesh install could not be exercised.
They are provided as validated *scaffolding*; the offline `sim` backend exercised the
full injection->observe->grade loop.

## Fixes applied during testing
- Self-test originally needed an explicit pod-kill observation (no `_sim_observe` entry
  for the self-fault case) — added a dedicated branch so all 5 experiments self-test.
- Confirmed `REPO = parents[4]` resolves to `/Users/mei/rl` (verified by path counting),
  so `from rex.scoring import deterministic_judge` imports the real shared grader.
