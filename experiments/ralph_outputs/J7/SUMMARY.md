# J7 — SUMMARY

**Task:** Run the agent against `gcp-bench` / `linode-bench` (live cloud scenarios).
Build/extend a runner that points the agent at those scenarios; run what's runnable
offline; document any live-cloud blocker precisely. No cloud cost, no live-resource
disruption, no shared-core edits.

## Result
- **Built** `artifacts/agent_bench_runner.py`: inserts the frozen-LLM agent (`agent.llm`)
  into the bench loop as an **action-selection policy**. For each of the 15 incidents it
  builds an SRE prompt from the CRE rule + symptom + a discrete action space (the gold
  runbook fixes), has the agent pick the fix, and scores it deterministically against the
  registry gold (no grading model). Works for both gcp and linode.
- **Ran offline (dry-run, $0):** gcp 13/15 = 0.867, linode 13/15 = 0.867; provider request
  assembles for 15/15 scenarios (proved via the pure `build_request` path, no API key).
- **Ran live LLM (no cloud):** minimax-m3 -> 3/15 = 0.2 (real Fireworks call); claude-haiku
  reached the endpoint but the Anthropic key is out of credits.
- **Tests:** `pytest` 5/5 passing, all offline.

## Live-cloud blocker (precise)
The bench's live 5-signal chain (metric->alert->CRE->action->recovery) cannot run: the temp
hackathon GCP account `devstar4126@gcplab.me` -- which `env.sh` pins for every gcloud call --
**has been deleted** (`invalid_grant: Account has been deleted`), so the GKE cluster is
gone and the saved kubeconfig is dead. Using a personal account would bill the user and
not reproduce the pinned project, so it was correctly refused. Re-running live needs a
fresh `gcloud auth login` to a credited account + `export GCP_PROJECT` + `stages/01..05`.

## Key finding
The agent IS pointed at the bench end-to-end (prompt -> LLM choice -> deterministic score),
stopping only at the impossible cloud apply. The offline action-selection metric is kept
explicitly separate from the live recovery reward to avoid over-claiming; the menu-leakage
caveat (gold fixes shown verbatim) is disclosed. minimax-m3's weak live score is partly a
provider artifact (base-completion endpoint ignores the chat system prompt).

## Artifacts
- `artifacts/agent_bench_runner.py`, `artifacts/test_agent_bench_runner.py`
- `artifacts/result_gcp_dryrun.json`, `artifacts/result_linode_dryrun.json`,
  `artifacts/result_gcp_live_minimax.json`
- `01..10` step files + this SUMMARY.

No shared core files were edited; all writes are under `experiments/ralph_outputs/J7/`.
