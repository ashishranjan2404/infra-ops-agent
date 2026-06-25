# G1 — SUMMARY

**Task:** Run SREGym (external live K8s benchmark, 90 problems) with our agent — direct
comparison. SREGym is not vendored here.

**Outcome:** Deliverable COMPLETED; downstream live run BLOCKED (no cluster). No scores fabricated.

## What was delivered
1. **Research brief** on SREGym's harness/interface (01, 04 §1), grounded in
   arXiv:2605.07161v1 + github.com/SREGym/SREGym + sregym.com: problem P=(E,I,F,O); MCP
   interface (Prometheus/Loki/Jaeger/kubectl + submission API); oracles O_d (9-question LLM
   checklist, tau=7/9) and O_m (programmatic recovery verifier); E2E = both; partitions
   ported 34 / similar 43 / new 13; `python main.py --agent <name> --model <litellm>`;
   agents sandboxed in Docker.
2. **Adapter design + scaffold** (artifacts/sregym_adapter.py): SREGymPlannerAdapter maps
   OUR plan-JSON policy onto SREGym's protocol — builds the prompt from a GATHERED
   observation bundle (no leaked spec), turns root_cause into the O_d diagnosis (victims
   labeled), translates each action into a kubectl/MCP command via a static tool-semantics
   table + a runtime target resolver. Reports out-of/partial-action-space and escalation
   honestly. Importable with no cluster/model/network.
3. **Translation table** (artifacts/action_translation.json): 13 tools, 9 expressible to
   kubectl, 4 inexpressible with explicit reasons.
4. **Tests** (artifacts/test_sregym_adapter.py): 10/10 pass.
5. **Run plan** (artifacts/run_plan.md) + **documented blocker** (artifacts/RUN_PLAN_blocker.md).

## Blocker (verified, not fabricated)
SREGym needs a live Kubernetes cluster + Docker + Helm + MCP stack + the SREGym repo —
none installed. Verified on-machine: kind and docker absent; the only kubectl context fails
auth. Plus a semantic gap: our agent is a non-interactive planner vs SREGym's interactive
MCP tool-users (a labeled transfer baseline), and 4/13 tools + non-K8s substrates are out of
our action space. No SREGym scores were produced or invented.
