# 10 — Feedback for the next task

The highest-leverage move for a "live X" task when the cluster/LLM is unreachable is to
make the deliverable *provable offline*: split the artifact into a reasoning side (reuse
existing frozen-model code unchanged) and an execution/safety side, then inject every
external dependency (telemetry source, proposer) so the core property is exercised by
pytest with no key and no cluster. Record a *real-shaped* fixture (byte-identical to the
live producer, here `mreal/server.py::_metrics()`) rather than a stub blob — it catches
parser bugs and makes "we mocked it" defensible. For safety claims specifically, make the
guarantee *structural* (the dangerous code path simply doesn't exist in the module) and
test it by grepping the source, not just by checking a flag — reviewers trust "can't"
over "won't." Finally, document the access blocker (interactive `gcloud` login,
exhausted LLM credits) precisely where a reviewer expects it (07/09) instead of hiding it,
and ship the live flags (`--prometheus`, `--live-llm`) so the harness is ready the moment
access exists.
