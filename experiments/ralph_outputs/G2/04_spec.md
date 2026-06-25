# G2 — Technical Spec

## 1. SREGym tool surface we emulate (5 families)
Mapped from SREGym's documented MCP servers onto our `sim.engine`:

| SREGym MCP server | Real SREGym backend | Our sim emulation |
|---|---|---|
| Metrics | Prometheus | `World.metric(node, key)` for `error_rate_pct`, `p99_latency_ms` over all nodes |
| Logs | Loki | `spec.observation.smoking_guns` (buried signature lines) + synthetic alert lines |
| Traces | Jaeger | edge list with propagated latency (best-effort; flagged low-fidelity) |
| Cluster control | `kubectl` | structured `{tool,args}` OR `kubectl`-string -> 25-verb registry translation |
| Submission | submit endpoint | `submit_diagnosis(text)` + `submit_mitigation()` -> `sim.engine.is_resolved` |

## 2. Adapter API (`sregym_adapter.py`)
A `SREGymEnv` class (in-process, importable) PLUS a thin JSON line protocol so an
external process (Stratus) could drive it. We implement the in-process class fully and
the line protocol as a documented thin wrapper (no network server needed for the proof).

```python
class SREGymEnv:
    def __init__(self, scenario_path: str, seed: int = 0): ...
    def reset(self) -> dict:
        # returns {"problem": str, "namespace": str, "phases": ["diagnosis","mitigation"]}
    # --- MCP tool families ---
    def get_metrics(self, node: str | None = None) -> dict:
        # {node: {"error_rate_pct": float, "p99_latency_ms": float}, ...}
    def get_logs(self, node: str | None = None, query: str = "") -> list[str]:
        # buried smoking-gun lines + noise; substring-filtered by `query`
    def get_traces(self, node: str | None = None) -> list[dict]:
        # [{"src","dst","latency_ms"}]  (low-fidelity; flagged)
    def cluster_control(self, command: str | None = None,
                        tool: str | None = None, args: dict | None = None) -> dict:
        # either a structured {tool,args} OR a kubectl-style `command` string.
        # returns {"applied": bool, "tool": <resolved>, "translated_from": <kubectl|None>,
        #          "untranslated": bool}
    def submit_diagnosis(self, text: str) -> dict:
        # {"diagnosis_correct": bool, "gold_root": str}
    def submit_mitigation(self) -> dict:
        # {"resolved": bool, "root_cleared": bool, "slo_ok": bool, "actions": [...]}
    # --- bookkeeping ---
    def fidelity(self) -> dict:
        # {"kubectl_calls": int, "untranslated_kubectl": int, "untranslated_rate": float}
```

### `kubectl` -> registry translation table (best-effort, lossy by design)
```
kubectl scale ... --replicas      -> scale_deployment(target=<obj>)
kubectl rollout undo              -> rollback_deployment(target=<obj>)
kubectl rollout restart           -> restart_service(target=<obj>)
kubectl delete pod                -> restart_pod(target=<obj>)
kubectl drain                     -> drain_node(target=<obj>)
kubectl cordon                    -> cordon_node(target=<obj>)
kubectl get|describe|logs|top     -> READ no-op (observation; not a mutation)
<anything else>                   -> untranslated=True  (counted toward fidelity gap)
```
Target object name is extracted from the command (`deploy/<x>`, `pod/<x>`, `<x>`), then
matched against scenario node names; unmatched target => untranslated.

## 3. Diagnosis grading (dep-free, deterministic)
SREGym diagnosis is NL root cause. We grade with a keyword-overlap check against the
scenario's gold root-cause node + kind (NO LLM judge, to keep the scaffold dep-free):
`diagnosis_correct` iff the submitted text mentions the fault node name AND a keyword of
the root-cause kind (e.g. `mem_leak` -> {memory, leak, oom, rss}). This is intentionally
strict-but-simple and documented as a stand-in for the real LLM judge.

## 4. Stub agent (`stub_agent.py`) — proof of the external loop
Deterministic SREGym-shaped client:
1. `reset()`, then `get_metrics()` to find the worst node, `get_logs()` to read the
   smoking gun.
2. `submit_diagnosis(<node> + <kind keyword>)`.
3. `cluster_control(tool=<canonical fix from spec>, args={target:<fault_node>})`.
4. `submit_mitigation()`; print the verdict + fidelity.
It also runs a **trap variant**: deliberately call the wrong tool to show the engine
refuses to resolve (proves the verdict is real, not hardcoded).

## 5. `agents.yaml` (SREGym schema)
```yaml
agents:
  - name: stratus
    kickoff_command: python -m clients.stratus.stratus_agent.driver.driver --server http://localhost:8000
    kickoff_workdir: .
    kickoff_env: null
  - name: cidg-stub          # our proof agent, same contract
    kickoff_command: python experiments/ralph_outputs/G2/artifacts/stub_agent.py --scenario scenarios/cidg/21-leaf-oom-positive.yaml
    kickoff_workdir: .
    kickoff_env: null
```

## 6. Test cases (`test_adapter.py`, pytest)
- `test_reset_returns_problem` — reset gives a non-empty problem + phases list.
- `test_metrics_reflect_fault` — the fault node's error_rate_pct > 0 at reset.
- `test_structured_fix_resolves` — canonical fix via structured cluster_control then
  submit_mitigation -> resolved True.
- `test_wrong_tool_does_not_resolve` — a non-remediating tool -> resolved False.
- `test_kubectl_translation` — `kubectl scale deploy/<fault> --replicas 5` translates to
  `scale_deployment`, `untranslated` False.
- `test_kubectl_untranslated_counted` — `kubectl edit configmap foo` -> untranslated
  True and fidelity counter increments.
- `test_diagnosis_grading` — correct NL mentions resolve `diagnosis_correct` True; an
  off-topic string -> False.

## 7. File formats
- All artifacts under `experiments/ralph_outputs/G2/artifacts/`.
- `agents.yaml` parseable by `yaml.safe_load`.
- Python files: stdlib + `yaml` + `sim` only; no new pip deps.
