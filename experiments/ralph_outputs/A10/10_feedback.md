# A10 — 10 Feedback for the next task

Validate the data's structural assumptions *before* designing the metric: I found
(only after computing) that every CIDG scenario's root cause reaches its entire
topology (`mean affected == mean topo size`), which makes a "blast radius" largely
redundant with topology size on this set. A 2-minute `python3` probe of the YAMLs up
front would have set expectations and let me frame the deliverable as "correct
propagation *mechanism* + sidecar plumbing" (which pays off on richer future
topologies) rather than over-claiming a discriminative severity signal. Also:
empirically pin down edge-direction semantics against one hand-checked scenario
before writing propagation code — it's a one-line correctness lever that's easy to
invert and hard to notice. Keep raw counts in the sidecar alongside any derived tier
so downstream consumers can re-bucket without rerunning. Finally, the
`scenarios/cidg/generated/` glob is 33 files (including `80-gitlab-db-deletion.yaml`),
not the 32 a numeric-prefix `ls` glance suggests — trust the glob count.
