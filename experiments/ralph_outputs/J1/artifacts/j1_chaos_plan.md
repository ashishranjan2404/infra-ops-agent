# J1 — Chaos-Injection Plan (Chaos Mesh)

## Goal
Inject **real infrastructure faults** into the `cidg-mreal` call-mesh so an SRE/REx
agent is evaluated on genuine, Prometheus-observable cascades instead of the scripted
`sim/engine.py` ones — while guaranteeing the faults never escape the namespace and
always auto-heal.

## Tool choice: Chaos Mesh vs Litmus
We chose **Chaos Mesh** because:
- Its CRD taxonomy (HTTPChaos / NetworkChaos / StressChaos / PodChaos) maps almost
  one-to-one onto our sim fault classes (error / latency / pool-exhaustion / availability),
  so the live experiments are direct twins of the offline ones.
- Namespace-scoped selectors + per-experiment `duration` give structural auto-heal with
  no extra controller config.
- HTTPChaos lets us fault at L7 (the same layer the app's `/ctl/fault` uses), giving a
  clean error/latency signal without editing the app.

Litmus was considered and is a fine alternative (richer "experiment + probe + verdict"
workflow), but its ChaosEngine/ChaosExperiment indirection is heavier than needed for a
5-fault eval sweep, and its fault primitives don't map as cleanly to our root-cause
classes. Decision: Chaos Mesh now; Litmus is a documented future option if we want
built-in probes/SLO verdicts.

## The fault ladder (fidelity levels — both kept)
- **L0 — app control plane (`/ctl/fault`)**: `POST payments:8080/ctl/fault?mode=error`.
  No Chaos Mesh needed; fastest smoke test; exercises the app's own fault path.
- **L1 — Chaos Mesh infra faults** (this plan): exercises the real kubelet/CNI/iptables
  path. Higher fidelity, the actual deliverable.
Note: HTTPChaos is highest-fidelity at L7 but is the most install-sensitive (needs the
Chaos Mesh interception enabled for target pods). NetworkChaos / StressChaos / PodChaos
operate at the CNI/kubelet layer and need no app cooperation — use them as the robust
fallback if HTTPChaos interception isn't available on the cluster.

## Install (one-time, in its own namespace)
```bash
export KUBECONFIG=gcp-bench/state/gke-kubeconfig.yaml
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm repo update
kubectl create ns chaos-mesh
helm install chaos-mesh chaos-mesh/chaos-mesh -n chaos-mesh \
  --set chaosDaemon.runtime=containerd \
  --set chaosDaemon.socketPath=/run/containerd/containerd.sock   # GKE default
kubectl -n chaos-mesh rollout status deploy/chaos-controller-manager
```

## Run an experiment (with auto-heal)
```bash
# preferred: drive it through the harness, which deletes the CR in a finally:
python3 experiments/ralph_outputs/J1/artifacts/j1_agent_runner.py \
  --backend kube --experiment j1-payments-error --soak 30 \
  --agent-cmd '<your agent command>'

# or manually (remember to delete to heal):
kubectl apply -f experiments/ralph_outputs/J1/artifacts/j1_chaos_experiments.yaml
# ... observe ...
kubectl -n cidg-mreal delete -f experiments/ralph_outputs/J1/artifacts/j1_chaos_experiments.yaml
```

## Safety contract (enforced structurally)
1. **Namespace-scoped**: every CR pins `selector.namespaces:[cidg-mreal]`. No
   cluster-wide, no kube-system/monitoring targeting.
2. **Time-bounded**: every fault has a `duration` (90–120s); pod-kill is instantaneous
   and the Deployment reschedules. A fault cannot outlive its window.
3. **Harness auto-heal**: `_kube_observe` deletes the experiment in a `finally`, so even
   a crashed run leaves no lingering fault.
4. **Least-privilege RBAC** (j1_staging_deploy.yaml): the runner SA may `create`/`delete`
   Chaos Mesh CRs and read/exec pods — but has **no delete on pods/deployments**. It can
   heal chaos, it cannot disrupt workloads.
5. **Do NOT tear down the live cluster** (per project notes — the GKE cluster must stay
   up through the week). This plan only adds/removes namespaced chaos CRs.

## Verification of auto-heal
```bash
kubectl -n cidg-mreal get httpchaos,networkchaos,stresschaos,podchaos
# expect: "No resources found" after the harness run completes.
```
