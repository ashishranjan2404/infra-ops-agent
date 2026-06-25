# J7 — 07 Test Results

## A. Live-cloud blocker — verified precisely (read-only checks, no cost)

### A.1 Temp GCP account is DELETED
```
$ gcloud projects list --account=devstar4126@gcplab.me
ERROR: (gcloud.projects.list) There was a problem refreshing your current auth tokens:
('invalid_grant: Account has been deleted',
 {'error': 'invalid_grant', 'error_description': 'Account has been deleted'})
```
The hackathon temp account (`devstar4126@gcplab.me`, the account `env.sh` pins for every
gcloud/kubectl call) has been deleted by GCP. There is no token to refresh.

### A.2 The GKE cluster is unreachable (gone with the account)
```
$ KUBECONFIG=gcp-bench/state/gke-kubeconfig.yaml kubectl get ns --request-timeout=10s
F0625 ... print credential failed ... Failed to retrieve access token:
  failure while executing gcloud ... (gcloud.config.config-helper) ...
  'invalid_grant: Account has been deleted'
```
The saved kubeconfig uses the gke-gcloud-auth-plugin exec credential against that dead
account → no cluster access.

### A.3 Why we do NOT work around it
- Credentialed local accounts are `ashishranjan2404@gmail.com` (personal) — using one to
  spin up a GKE cluster would **bill the user** and violates the task's "no cloud cost /
  no live-resource disruption" constraint, AND would not reproduce the bench's pinned
  project. So the live 5-signal chain (metric→alert→CRE→action→recovery) cannot run.

**BLOCKER (precise):** the live loop requires the deleted hackathon GCP account + its
now-gone GKE cluster. Re-running live needs a fresh `gcloud auth login` to a credited
account and `export GCP_PROJECT=<id>`, then `stages/01..05` (~$0.30/hr GKE). Out of scope
for a no-cost run.

## B. Offline runner — RUNS, real numbers

### B.1 Dry-run (offline, $0), both benches
```
$ python3 artifacts/agent_bench_runner.py --bench gcp --dry-run
  gcp-bench [dry-run]: action-select accuracy 13/15 = 0.867  (cloud_executed=False)
$ python3 artifacts/agent_bench_runner.py --bench linode --dry-run
  linode-bench [dry-run]: action-select accuracy 13/15 = 0.867  (cloud_executed=False)
```
- `request_assembled = 15/15` for both → the agent's provider wiring builds a valid
  request for every scenario, offline, with no API key.
- Baseline misses: `bad_deploy_errors`, `db_pool_exhaustion` (both fix via `rollout undo`
  / pod kill whose tokens don't overlap the service name → expected lexical baseline miss).

### B.2 Live agent (real LLM call, still NO cloud)
```
$ python3 artifacts/agent_bench_runner.py --bench gcp --live-agent claude-haiku-4-5
  requests.exceptions.HTTPError: 400 Client Error: Bad Request  (api.anthropic.com/v1/messages)
```
→ Anthropic key is out of credits (known, per project memory). The call path is correct —
it reached the real endpoint and got a real 400. Not a code defect.

```
$ python3 artifacts/agent_bench_runner.py --bench gcp --live-agent minimax-m3
  LIVE minimax-m3 gcp: correct=3/15 = 0.2  (cloud_executed=False)
```
→ Real live LLM run via Fireworks. Finding: `minimax-m3` is served on the `/completions`
(base-completion) endpoint, so the chat `system` prompt is not honored and most replies
are empty under `max_tokens=16`; 3/15 parsed to a correct integer. This is genuine agent
output, deterministically scored, with the cluster never touched.

## C. Unit tests (offline)
```
$ python3 -m pytest artifacts/test_agent_bench_runner.py -q
.....                                                                    [100%]
5 passed in 0.03s
```

## Summary table
| run                       | mode      | n  | correct | accuracy | cloud touched |
|---------------------------|-----------|----|---------|----------|---------------|
| gcp-bench                 | dry-run   | 15 | 13      | 0.867    | no            |
| linode-bench              | dry-run   | 15 | 13      | 0.867    | no            |
| gcp-bench (minimax-m3)    | live-agent| 15 | 3       | 0.200    | no            |
| gcp-bench (claude-haiku)  | live-agent| 15 | —       | (credits)| no            |
| pytest                    | —         | 5  | 5 pass  | —        | no            |

chance rate ≈ 1/15 = 0.067.
