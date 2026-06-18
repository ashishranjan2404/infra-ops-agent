"""End-to-end runner — runs many (service, fault) scenarios, scores them.

This is the headline script. It:
  1. picks N scenarios (one per incident type × a deterministic service)
  2. injects each into the cluster simulator
  3. drives the agent reasoning loop against it
  4. scores the trace with `verify/score.py`
  5. writes traces + metrics + scores to /Users/mei/rl/runs/<scenario>/

Designed so you can do:
  python -m run_e2e --n 15 --out runs/website-demo
and get everything the website needs: traces.json, scores.json, metrics.csv,
plus a `demo_traces.json` curated subset for the homepage.

Three modes:
  --mode baseline  : stub LLM (the dataset's "ground-truth" plan)
  --mode random    : stub LLM with shuffled tool order (a "broken" baseline)
  --mode model     : real Claude API (if ANTHROPIC_API_KEY set)
"""
from __future__ import annotations
import json, sys, time, argparse, random, hashlib
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sim.cluster import ClusterSim, SERVICE_METRICS
from agent.runtime import AgentRuntime, RunTrace
from agent.llm import llm_call, parse_response, stub_plan
from verify.score import verify_trace, aggregate
from metrics.collect import collect as collect_metrics


# 15 incident types × a deterministic service each
SCENARIOS = [
    ("cart",         "oom_kill"),
    ("checkout",     "crashloop"),
    ("gateway",      "latency_spike"),
    ("payments",     "bad_deploy_errors"),
    ("billing",      "disk_pressure"),
    ("auth",         "cert_expiry"),
    ("recommendations", "memory_leak"),
    ("inventory",    "db_pool_exhaustion"),
    ("orders",       "node_not_ready"),
    ("notifications","consumer_lag"),
    ("search",       "dns_failure"),
    ("user-profile", "upstream_5xx"),
    ("media-upload", "cpu_saturation"),
    ("shipping",     "stuck_rollout"),
    ("sessions",     "cache_stampede"),
]


def run_scenario(service: str, fault: str, model: str, seed: int,
                 duration_s: float = 120.0) -> RunTrace:
    sim = ClusterSim(seed=seed, duration_s=duration_s)
    sim.boot()
    inc = sim.inject(fault, service=service, duration_s=duration_s)
    rt = AgentRuntime(sim, model=model, max_steps=8)
    return rt.run(inc)


def make_broken_stub(messages, temperature=0.0):
    """A deliberately broken policy: skips diagnosis, jumps straight to a
    plausible-sounding but wrong tool. Used to show the verifier catching it.
    """
    inc_msg = next((m for m in messages if m.role == "user" and "INCIDENT:" in m.content), None)
    if not inc_msg:
        from agent.llm import LLMResponse
        return LLMResponse(text="Action: restart_pod({})", model="stub-broken", input_tokens=0, output_tokens=10, latency_ms=1)
    import json as _json, random as _r
    payload = _json.loads(inc_msg.content.split("INCIDENT:\n", 1)[1].split("\n\nResolve")[0])
    svc = payload.get("service_id", "checkout")
    n_calls = sum(1 for m in messages if m.role == "user" and "TOOL_RESULT" in m.content)
    # Always restart_pod first — wrong for most incident types
    if n_calls == 0:
        text = (f"Thought: Looks like a pod issue on {svc}. Just restart it and see.\n"
                f"Action: restart_pod({_json.dumps({'service_id': svc})})")
    else:
        text = f"Thought: Restarted. Should be fixed.\nAction: end_incident({_json.dumps({'service_id': svc})})"
    from agent.llm import LLMResponse
    return LLMResponse(text=text, model="stub-broken", input_tokens=200, output_tokens=len(text)//4, latency_ms=2)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=15, help="scenarios to run (max 15, one per incident type)")
    ap.add_argument("--out", default="runs/website-demo", help="output directory")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--duration", type=float, default=120.0)
    ap.add_argument("--model", default="stub", help="stub | stub-broken | claude-sonnet-4-5")
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "traces").mkdir(exist_ok=True)
    (out / "metrics").mkdir(exist_ok=True)

    # 1) Run all scenarios
    print(f"=== running {args.n} scenarios (model={args.model}) ===")
    all_reports = []
    traces_for_site = []
    for i, (svc, fault) in enumerate(SCENARIOS[: args.n]):
        # Inject llm_call swap if "stub-broken" mode
        import agent.llm as llm_mod
        original_call = llm_mod.llm_call
        if args.model == "stub-broken":
            llm_mod.llm_call = lambda msgs, model="x", temperature=0.0: make_broken_stub(msgs, temperature)
        try:
            t0 = time.time()
            trace = run_scenario(svc, fault, args.model, args.seed + i, args.duration)
            dt = time.time() - t0
            score = verify_trace(trace)
            score["scenario"] = f"{svc}_{fault}"
            score["trace_file"] = f"traces/{svc}_{fault}.json"
            all_reports.append(score)
            # save trace
            trace_path = out / "traces" / f"{svc}_{fault}.json"
            trace_path.write_text(json.dumps(trace.to_dict(), indent=2, default=str))
            # save metrics CSV for this scenario (RCAEval format)
            metrics_dir = out / "metrics" / svc / fault / str(int(time.time()))
            collect_metrics(metrics_dir, svc, fault, duration_s=min(60.0, args.duration),
                            seed=args.seed + i, dt=1.0)
            status = "✓" if score["reward"] else "✗"
            print(f"  [{i+1:2d}/{args.n}] {status}  {svc}_{fault:24s}  "
                  f"resolved={score['resolved']}  fix={score['fix_tool']}  "
                  f"reward={score['reward']}  steps={score['n_steps']}  "
                  f"({dt:.2f}s)")
            # save a curated subset for the website
            if i < 6:
                traces_for_site.append({
                    "scenario": f"{svc}_{fault}",
                    "service": svc, "fault": fault,
                    "incident": trace.incident,
                    "steps": [s.to_dict() for s in trace.steps],
                    "final": trace.final,
                    "resolved": trace.resolved,
                    "reward": score["reward"],
                    "process_quality": score["process_quality"],
                })
        finally:
            llm_mod.llm_call = original_call

    # 2) Aggregate
    print()
    print("=== AGGREGATE ===")
    agg = aggregate(all_reports)
    print(f"  n={agg['n']}")
    print(f"  resolved_rate     = {agg['resolved_rate']:.0%}")
    print(f"  action_correct    = {agg['action_correct_rate']:.0%}")
    print(f"  reward_rate       = {agg['reward_rate']:.0%}")
    print(f"  process_quality   = {agg['process_quality_mean']:.2f} / 1.0")
    print(f"  mean steps        = {agg['steps_mean']:.1f}")
    print(f"  mean tokens       = {agg['tokens_mean']:.0f}")

    # 3) Persist
    (out / "scores.json").write_text(json.dumps({"reports": all_reports, "aggregate": agg}, indent=2))
    (out / "demo_traces.json").write_text(json.dumps(traces_for_site, indent=2))
    print(f"\nwrote → {out}/scores.json + demo_traces.json + traces/ + metrics/")
    return agg


if __name__ == "__main__":
    main()
