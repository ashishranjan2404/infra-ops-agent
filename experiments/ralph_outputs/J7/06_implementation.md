# J7 — 06 Implementation

## What I built (all task-namespaced; no shared core file edited)

### `artifacts/agent_bench_runner.py`
A runner that points the frozen-LLM agent (`agent.llm`) at the `gcp-bench` and
`linode-bench` scenarios as an **action-selection policy**:
- Loads each `registry.json` read-only (15 non-skipped scenarios each).
- Builds a discrete action space = deduped union of the 15 gold runbook fixes.
- For each incident, assembles an SRE prompt from the CRE rule (`scenarios/cre-*.yaml`)
  + the `log_marker` symptom + the numbered candidate actions.
- Picks an action via one of two policies:
  - **dry-run** (default, offline, $0): proves the provider request assembles via
    `agent.llm.build_request` (pure, no network) for every scenario, then scores a
    deterministic lexical baseline policy.
  - **live-agent MODEL**: real `agent.llm.call(MODEL, ...)`, parses the chosen index.
- Scores deterministically: `correct = (chosen == gold)`,
  `action_select_accuracy = correct/n`.
- Records the chosen kubectl command per row with `cloud_applied=false` and a blocker
  reason. **Never** runs gcloud/kubectl; **never** executes the chosen command.

### `artifacts/test_agent_bench_runner.py`
5 offline tests (registry load, action-space dedupe/coverage, prompt shape, offline
request assembly, deterministic cloud-free run). All pass.

### Outputs produced (real)
- `artifacts/result_gcp_dryrun.json` — gcp, baseline, 13/15 = 0.867.
- `artifacts/result_linode_dryrun.json` — linode, baseline, 13/15 = 0.867.
- `artifacts/result_gcp_live_minimax.json` — gcp, **live LLM** (minimax-m3), 3/15 = 0.2.

## How this inserts the agent into the existing bench loop
The bench's `stages/06_run_scenario.sh` does `eval "$(cat "$FIX_FILE")"` where `$FIX_FILE`
is the *hardcoded* registry `fix`. This runner produces the agent's `chosen_action_cmd`,
which is exactly the string that would replace that hardcoded fix when a live cluster
exists. The wiring into stage 06 is documented (not patched, per the no-core-edit rule):

> In `06_run_scenario.sh` step (f), replace the registry-`fix` source with
> `agent_bench_runner.py --live-agent $MODEL`'s `chosen_action_cmd` for that scenario.

No `.patch` was needed to a core *Python* file; the integration point is a shell stage
owned by the bench, and the brief forbids editing it — so it is described, not modified.

## What I did NOT do (and why)
- Did not provision/contact any cluster (cost + the cluster is gone — see 07).
- Did not edit `agent/*.py`, `rex/*.py`, `sim/*.py`, `stages/*.sh`, or any registry.
- Did not run the live Anthropic model to completion (key out of credits — see 07).
