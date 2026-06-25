# J1 — 10 Feedback for the next task

The biggest lesson: for any task that names a *live* resource (cluster, API, GPU),
**probe access in the first two minutes** before designing — a 6-second `curl --max-time`
to the API server and a `gcloud config config-helper` call instantly revealed both
blockers (dead account + firewalled endpoint) here, which would otherwise have surfaced
only after writing everything. The project's GKE access is currently broken (gcloud
account `devstar4126@gcplab.me` deleted, API server `136.114.32.127` unreachable), so
any future cluster-touching task (deploy, scale, scrape) should assume offline and lead
with a sim/dry-run twin; switching gcloud accounts is risky shared global state and the
endpoint is unreachable regardless. Second lesson: the strongest offline deliverable for
an infra task is a harness with a **shared grader across a real and a simulated backend**
— it makes the offline run a true twin of the live one and keeps results comparable, so
a blocked live step still leaves a usable artifact. Finally, `kubectl --dry-run=client`
is NOT offline (it needs the API server for its RESTMapper, and the project kubeconfig's
exec-cred plugin fails before that) — use `yaml.safe_load_all` + per-kind required-field
assertions for genuinely offline manifest validation.
