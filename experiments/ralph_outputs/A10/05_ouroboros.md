# A10 — 05 Ouroboros (self-critique as 3 different engineers)

## Engineer 1 — Graph-correctness reviewer
**Problem found**: The spec said "fault flows to callers" but I must be certain the
YAML edge convention is `from depends on to`. If it were the reverse, every blast
radius is inverted. **Resolution**: validated empirically — in
slack-consul-cache-db, `ingress-gw → consul-agent` with the root cause AT
consul-agent and `assertions.cascades: true`; the only way the cascade reaches
4 nodes is reverse reachability. Encoded as `test_real_scenario_consul`. Also: a
cycle in edges would infinite-loop a naive walk — BFS with a `seen` set handles it.

## Engineer 2 — Metric-semantics reviewer
**Problem found**: Tiering risks degeneracy — with topologies capped at 5 nodes and
most real-incident scenarios fully connected, `n>=4` makes nearly all of them SEV1,
collapsing the tier's discriminative value. **Resolution**: this is a *real finding
about the data*, not a bug: the synthetic single-node scenarios correctly land SEV3,
and the historical multi-service cascades land SEV1 — which is honest. I documented
the skew (24 SEV1 / 1 SEV2 / 8 SEV3) in verification rather than hiding it, and I
kept `services_affected_pct` and raw counts so downstream users can re-tier if they
want finer granularity. Tier is a convenience label, the count is the primary signal.

## Engineer 3 — Reproducibility / packaging reviewer
**Problem found**: (a) `REPO_ROOT` derived by walking `..` four times is brittle if
the file is moved; (b) output written next to the script could collide if run twice
— but it's idempotent (overwrite), so acceptable; (c) the script must not import
anything outside stdlib + pyyaml. **Resolution**: confirmed only `yaml` is external
(already a repo dep); path derivation is anchored to `__file__` and verified by the
real-scenario test actually finding the YAML. Added a "no scenarios found" guard
returning non-zero so a broken path fails loudly instead of writing an empty sidecar.

## Final filtered spec (unchanged from 04 except)
- Explicit cycle-safety via `seen` set (was implicit).
- Loud failure (exit 1) when scenario glob is empty.
- Tier documented as a convenience label over the primary count signal; data skew
  is reported, not engineered away.
