# G1 — Honest critique

## What a reviewer attacks
1. **No scores, so no comparison actually happened.** The task title says "direct
   comparison on their 90 problems." We did not run a single problem. The honest defense:
   SREGym is a live-cluster benchmark that is genuinely not installable in this session
   (verified: no kind/docker, dead kubectl). Per the brief, a correct scaffold + honest
   blocker beats fabricated numbers — but a reviewer is right that the headline goal is
   unmet. This is a BLOCKED downstream run, not a completed comparison.

2. **The integration seam is unverified.** `SREGymClient` / the `--agent` registration /
   the three `Sregym*` glue classes are written against the PUBLIC description of SREGym's
   API, not its actual source (whose submission-API symbols aren't published). If SREGym's
   `BaseAgent.solve` signature differs, the run_plan snippet needs edits. The Protocol is
   deliberately minimal to limit this risk, but it's an assumption, not a tested fact.

3. **The semantic gap may make any future comparison weak.** Even fully unblocked, our
   non-interactive planner is a different class of agent from the interactive tool-users on
   the leaderboard. The result would be a labeled transfer baseline. A skeptic can argue the
   most honest number ("how far does a pure planner get on a live benchmark") is interesting
   but not a leaderboard-beating headline.

4. **Action-space coverage is genuinely partial.** 4/13 of our tools are inexpressible, and
   whole substrates (TiDB/MongoDB/Kafka/OS/hardware) are out of scope. On the 90-problem set,
   a meaningful fraction will be N/A. The adapter reports this honestly, but it caps our
   achievable mitigation-rate — our agent simply can't act on those problems.

5. **`build_diagnosis` is shallow vs O_d's 9-question rubric.** It puts the originating
   component first and labels victims, but it does not explicitly populate "fault
   characterization" details (ports, env vars) that O_d checks — those would have to come
   from the gathered observation, which our offline stub doesn't model richly.

## What's weak / missing
- No live feedback loop in the offline scaffold (refinement is a no-op until a cluster
  exists), so the adapter under-uses our REx policy's strength (iterative refinement).
- The observation gatherer is a stub; the real MCP query logic is unwritten (it's
  SREGym-API-shaped and can't be written without the install).
- No cost/latency/token accounting (SREGym reports T-T-D / T-T-M / tokens).

## Fair overall assessment
Solid, validated bridge engineering with an honest, verified blocker. NOT the requested
end result (real scores on 90 problems). Status: deliverable completed, downstream run
blocked. No fabrication anywhere.
