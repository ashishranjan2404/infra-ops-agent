# G1 — Technical Spec

## 1. SREGym interface contract (the surface we bind to)

```
Problem P = (E, I, F, O)
  E  live K8s environment (app deployed; faults injected)
  I  agent interface: MCP servers {metrics(Prometheus), logs(Loki),
       traces(Jaeger), cluster-control(kubectl), submission(API)}
  F  injected faults + ambient noises
  O  oracles: O_d (diagnosis), O_m (mitigation)

Protocol (one run):
  1. observe(E via I)
  2. submit_diagnosis(nl_text)      -> O_d  (LLM checklist, 9 Qs / 3 dims, tau=7/9)
  3. mitigate(actions on cluster)
  4. signal_done()                  -> O_m  (programmatic recovery verifier)
  E2E = O_d AND O_m on the same run.

Invocation: python main.py --agent <name> --model <litellm-string>
Agents run inside an isolated Docker container; cannot read F/O.
Partitions: ported=34, similar=43, new=13 (total 90). 3 runs/problem.
```

(Source: arXiv:2605.07161v1; github.com/SREGym/SREGym; sregym.com. The exact Python
class/function names of the submission API are NOT published in the public excerpt —
the adapter therefore targets a small, documented `SREGymClient` Protocol that a real
integrator binds to SREGym's `BaseAgent`/submission API at install time. See blocker.)

## 2. Adapter module: `sregym_adapter.py`

### 2.1 Protocols (what SREGym must provide; stubbed offline)
```python
class ObservationGatherer(Protocol):
    def gather(self, problem_id: str) -> dict:
        # -> {"alert": str, "metrics": {...}, "logs": [str], "traces": [...],
        #     "topology": [{"src","dst","type"}], "targets": [str]}
        ...

class TargetResolver(Protocol):
    def resolve(self, logical_target: str) -> dict:
        # -> {"namespace": str, "kind": "deployment"|"statefulset"|..., "name": str}
        ...

class SREGymClient(Protocol):          # bound to SREGym's real submission API at install
    def submit_diagnosis(self, text: str) -> dict: ...
    def run_command(self, argv: list[str]) -> dict: ...   # kubectl/MCP control
    def signal_done(self) -> dict: ...
```

### 2.2 Plan policy injection
```python
ProposeFn = Callable[[Scenario|None, str|None], dict]   # our rex proposer
# default propose uses agent.llm.call(model, build_prompt(...)) -> parse_plan
```

### 2.3 Core class
```python
@dataclass
class SREGymPlannerAdapter:
    propose_fn: ProposeFn
    gatherer: ObservationGatherer
    resolver: TargetResolver
    translation: dict          # loaded from action_translation.json
    budget: int = 4            # REx refinement budget (no live feedback offline)

    def build_diagnosis(self, plan: dict) -> str
    def translate_action(self, action: dict) -> dict
        # -> {"expressible": bool, "argv": list[str]|None,
        #     "tool": str, "reason": str}
    def translate_plan(self, plan: dict) -> dict
        # -> {"commands": [argv...], "skipped": [{action,reason}],
        #     "out_of_action_space": bool}
    def run_problem(self, problem_id: str, client=None, dry_run=True) -> dict
```

### 2.4 `run_problem` returns (the per-problem record)
```json
{
  "problem_id": "ported-0007",
  "entry_kind": "non-interactive planner (transfer)",
  "observation_used": true,
  "diagnosis_text": "service-control control plane crash-looping ...",
  "plan": {"root_cause": "...", "actions": [...]},
  "commands": [["kubectl","-n","ns","scale","deployment/x","--replicas","3"]],
  "skipped": [{"action": {...}, "reason": "out of action space"}],
  "out_of_action_space": false,
  "escalated": false,
  "submitted": false,
  "dry_run": true,
  "caveat": "non-interactive planner; SREGym reference agents are interactive MCP tool-users"
}
```

## 3. Action translation table (`action_translation.json`)
Maps each of our 12 remediation tools to a kubectl/MCP command TEMPLATE and an
`expressible` flag. `{ns}` / `{kind}` / `{name}` are filled by `TargetResolver`.
Tools without a faithful generic kubectl mapping (`modify_network_policy`,
`renew_certificate`, `clear_cache`) are marked `expressible:false` with a reason,
because their real fix is problem-specific (a particular NetworkPolicy / Secret /
cache endpoint) that cannot be synthesized generically. This is the honest
action-space-gap boundary.

## 4. Metrics (run plan emits these; never escalation alone)
```
diagnosis_rate, mitigation_rate, e2e_rate,
harmful_mitigation_rate  (mitigations that fired a trap / worsened state),
escalation_rate, out_of_action_space_count,
per-partition (ported/similar/new) splits.
```

## 5. Test cases (`test_sregym_adapter.py`)
- T1 import: module + class import cleanly.
- T2 translate every tool: each of the 12 tools yields a record; expressible ones
  produce a non-empty argv; inexpressible ones set `expressible:false` + a reason.
- T3 diagnosis: `build_diagnosis` returns the plan's `root_cause` non-empty.
- T4 dry-run `run_problem`: returns the full contract dict with `submitted=false`,
  `dry_run=true`, and a `caveat`.
- T5 out-of-action-space: a plan whose only action is inexpressible sets
  `out_of_action_space=true`.
- T6 escalation pass-through: an empty-actions plan sets `escalated=true`.
- T7 resolver binding: a translated expressible command contains the resolved
  namespace + name from the StubResolver.

## 6. File formats
- `action_translation.json`: `{tool: {"expressible": bool, "argv_template":[...],
  "treats": str|null, "reason": str|null}}`.
- All `.md` parseable; `result.json` one line per the brief.
