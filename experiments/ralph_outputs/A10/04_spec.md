# A10 — 04 Spec

## Input
`scenarios/cidg/generated/*.yaml`. Relevant fields:
- `meta.id` (str) — incident id (sidecar key).
- `topology.nodes[].name` (str), `topology.edges[] = {from, to, type, weight,...}`.
- `root_cause.location` (str, a node name), `root_cause.severity` (float 0–1).
- `assertions.cascades` (bool).

## Edge semantics (contract)
`{from: A, to: B}` ⇒ A depends on B (A calls B). Fault impact flows opposite to
dependency: a fault at N reaches all nodes that depend on N ⇒ reverse reachability.

## Core function signatures
```python
def reverse_reachable(root: str, edges: list[tuple[str,str]]) -> set[str]
    # BFS over reversed edges (to->from); returns affected set INCLUDING root.

def severity_tier(n_affected: int, rc_sev: float, cascades: bool) -> str
    # "SEV1" | "SEV2" | "SEV3"

def compute_for_scenario(path: str) -> dict   # one incident record
def main() -> int                              # writes JSON+CSV, prints summary
```

## Output record schema (per incident, in JSON)
```json
{
  "incident_id": "slack-consul-cache-db",
  "file": "scenarios/cidg/generated/54-...yaml",
  "root_cause_node": "consul-agent",
  "root_cause_severity": 0.7,
  "cascades": true,
  "total_services": 4,
  "services_affected": 4,
  "services_affected_pct": 100.0,
  "affected_services": ["cache-ring","consul-agent","ingress-gw","vitess-db"],
  "severity_tier": "SEV1"
}
```
JSON top level: `{"count": N, "incidents": [ ... ]}`.

## CSV columns
`incident_id, root_cause_node, total_services, services_affected,
services_affected_pct, severity_tier, cascades, affected_services` (pipe-joined).

## Tier rule
- SEV1: `n>=4` OR (`rc_sev>=0.9` AND cascades)
- SEV2: `n>=2` OR cascades
- SEV3: otherwise (single contained service)

## Edge cases
- Empty `edges` ⇒ affected = {root} (the 8 synthetic single-node scenarios → SEV3).
- `root` not in nodes ⇒ affected = [root] (defensive; should not occur in data).
- Edges referencing unknown nodes ⇒ dropped before BFS.

## Test cases (`test_blast_radius.py`)
1. Linear chain A→B→C (A dep B dep C), fault at C ⇒ {A,B,C}.
2. Fault at A (leaf caller) ⇒ {A} only.
3. Fan-out: B→A, C→A, fault at A ⇒ {A,B,C}.
4. No edges, single node ⇒ {root}, tier SEV3.
5. severity_tier boundaries: (4,0.7,False)→SEV1; (2,0.1,False)→SEV2;
   (1,0.95,True)→SEV2 (n<4, sev>=0.9+cascade only lifts to... ) — see test.
6. Real scenario slack-consul-cache-db ⇒ 4 affected, SEV1.
