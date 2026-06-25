# G1 — Feedback for the next task

External live benchmarks (SREGym, AIOpsLab, ITBench) share the same wall: they need a
running Kubernetes cluster + Docker + MCP observability stack that simply isn't present in
this session (verified: no kind/docker, dead kubectl auth). The high-leverage move is NOT
to chase the install but to ship the BRIDGE: a precise interface brief grounded in the
paper/repo (cite arXiv + GitHub + the site), a small importable adapter that translates our
plan-JSON policy onto their submission protocol, a runtime resolver for per-problem resource
names, and an honestly-tagged action-space gap (mark inexpressible tools and out-of-substrate
problems as N/A, never fake or silently-zero them). Two recurring traps to pre-empt:
(1) `str.format` on templates containing literal JSON `{}` braces — use a sentinel; (2) the
validity hazard of feeding our agent a leaked spec — always build the prompt from a GATHERED
observation bundle so we don't consume structure the benchmark deliberately withholds. Frame
any cross-harness comparison as a labeled non-interactive transfer baseline, and report
escalation paired with solve-rate, never alone. Note B15 already froze SREGym's published
leaderboard numbers, so G1 and B15 compose: B15 = the target numbers, G1 = the harness to
go get our own. A future unblocked task only needs a kind cluster + the three `Sregym*` glue
classes.
