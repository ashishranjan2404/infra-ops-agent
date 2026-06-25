# J1 — 04 Technical Spec

## A. Topology (from mreal/k8s.yaml — authoritative)
```
gateway --> checkout --> payments --> db(pool, 8 slots)
                          orders   --> db(pool)            (fan-in)
```
Fault at payments => checkout 500 => gateway 500 (gateway = loud victim).

## B. Chaos experiments (j1_chaos_experiments.yaml)
| name | CRD | maps to sim fault | scope | bound |
|------|-----|-------------------|-------|-------|
| j1-payments-error | HTTPChaos abort | "error" at root | app=payments, mode=all | 90s |
| j1-payments-latency | HTTPChaos delay 1200ms | "slow" at root | app=payments, mode=all | 120s |
| j1-db-pool-stress | StressChaos cpu | pool exhaustion (fan-in) | app=db, mode=one | 120s |
| j1-checkout-egress-delay | NetworkChaos delay 800ms | partial degradation / red herring | app=checkout->payments | 120s |
| j1-gateway-pod-kill | PodChaos pod-kill | availability self-fault | app=gateway, mode=one | instant |

Every CR: `selector.namespaces:[cidg-mreal]` (never cluster-wide); bounded duration
(except pod-kill which is instantaneous + self-recovering via the Deployment).

## C. Harness data structures (j1_agent_runner.py)
```python
@dataclass
class Observation:
    experiment: str
    per_app: dict          # app -> {"err_rate": float|None, "p50_s": float|None, "up": bool}
    loudest_victim: str
    notes: str

GROUND_TRUTH: dict[str, tuple[str, list[str]]]
    # experiment -> (gold_root_cause_text, [red_herring_terms])
```

## D. Function signatures
```python
def _sim_observe(experiment: str) -> Observation          # offline twin via topology
def _kube_observe(experiment: str, soak_s=30) -> Observation  # live: apply/scrape/heal
def _parse_metrics(text: str, app: str) -> dict           # Prometheus text -> err_rate
def run_agent(agent_cmd: str, obs: Observation) -> str    # obs JSON on stdin -> diagnosis stdout
def score(experiment: str, diagnosis: str) -> bool        # rex.scoring.deterministic_judge
def selftest() -> int                                     # 0 if all oracle/herring asserts pass
def main() -> int
```

## E. Agent contract
The agent-under-test is any shell command. Harness writes `json.dumps(asdict(obs))`
to its **stdin**; the agent prints a one-line **root-cause diagnosis** to **stdout**.
This makes any REx/LLM agent or a baseline `echo` swappable without code change.

## F. Scoring contract
`score()` delegates to `rex.scoring.deterministic_judge(diagnosis, gold, red_herrings)`
— the same grader used across the project. Offline fallback (token overlap with gold,
red-herring penalty) only if the import is unavailable.

## G. Test cases
1. `selftest`: for each experiment, `score(gold)==True` and
   `score("the <herring> is the problem")==False`, and `loudest_victim` non-empty. (5×)
2. RBAC invariant: Role allows `delete` on `chaos-mesh.org` resources, **not** on `""`
   (pods/deployments).
3. Manifest structural: required fields present per kind; multi-doc parses to the
   expected kind list.
4. Live (LIVE only): apply -> soak -> scrape returns per-app err_rate; experiment is
   deleted after (auto-heal verified by `kubectl get httpchaos` empty).

## H. File formats
- Chaos + deploy: standard multi-doc Kubernetes YAML.
- Harness output: JSON `{"backend","results":[{experiment,loudest_victim,diagnosis,passed,obs}]}`.
