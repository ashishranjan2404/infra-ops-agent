"""Verifier glue — turns a RunTrace into the same reward the dataset uses.

The dataset's `verify.py` (in infra-agent/) checks three things from a recorded
trajectory:
  1. resolved    — the metric crosses back under its SLO threshold
  2. action_correct — the fix tool matches the canonical fix for that incident type
  3. guardrail_ok — if the tool needs approval, a human granted it

We do the same here for a live (or simulated) RunTrace, plus report the
"process" signals the binary verifier can't see (skipped diagnosis, hallucinated
args, thought/action mismatch) — the same signals the DPO pairs were built
to capture.

Outputs:
  - per-run: {resolved, action_correct, guardrail_ok, reward}
  - per-run process: {diagnosed_first, args_match, thought_action_aligned}
  - aggregate: resolve rate, action-correct rate, mean steps, mean tokens
"""
from __future__ import annotations
import json, sys, argparse
from pathlib import Path
from collections import Counter
from typing import Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from agent.runtime import RunTrace, Step


def verify_trace(trace: RunTrace) -> dict:
    """Score one trace with the same reward the dataset uses."""
    inc = trace.incident
    fix_tool = inc["type"]  # we'll resolve against the canonical fix below
    steps = trace.steps

    # Find the first non-diagnostic action (the "fix" attempt)
    diag_tools = {"get_metrics", "get_logs", "get_events", "describe_pod",
                  "get_deployment_status", "get_node_status", "query_traces", "get_alerts"}
    fix_step = next((s for s in steps if s.role == "assistant" and s.tool not in diag_tools), None)

    # resolved — from the runtime's final verifier pass
    resolved = trace.resolved

    # action_correct — does the fix tool match the canonical fix?
    import os as _os
    _INFRA = _os.environ.get(
        "INFRA_AGENT_PATH",
        str(Path(__file__).resolve().parents[2] / "ashish-life-os" / "hackathons" / "inference-time" / "infra-agent"),
    )
    if _INFRA not in sys.path:
        sys.path.insert(0, _INFRA)
    from generate import INCIDENTS, TRUST  # type: ignore
    canonical_fix = next(i["fix"] for i in INCIDENTS if i["type"] == inc["type"])
    fix_name = fix_step.tool if fix_step else ""
    action_correct = (fix_name == canonical_fix)

    # guardrail_ok — if the canonical fix needed approval, was it granted?
    tier = TRUST.get(canonical_fix, "autonomous")
    if tier == "autonomous":
        guardrail_ok = True
    else:
        if fix_step:
            approval = fix_step.approval or "auto"
            guardrail_ok = approval == "granted_by_human"
        else:
            guardrail_ok = False

    # binary reward (matches verify.py exactly)
    reward = int(resolved and action_correct and guardrail_ok)

    # --- process signals the binary verifier can't see ---
    # 1. diagnosed_first — at least one diagnostic tool was called BEFORE the fix
    first_fix_idx = next((i for i, s in enumerate(steps)
                          if s.role == "assistant" and s.tool not in diag_tools), len(steps))
    diagnosed_first = any(s.role == "assistant" and s.tool in diag_tools
                          for s in steps[:first_fix_idx])
    # 2. args_match — the args included the correct service_id from the incident
    args_match = any(s.role == "assistant" and s.args.get("service_id") == inc["service"]
                     for s in steps if s.tool != "end_incident")
    # 3. thought_action_aligned — every step's thought mentions a relevant concept
    keywords = {
        "oom_kill": ["memory", "OOM", "limit"],
        "crashloop": ["crash", "rollback", "config"],
        "latency_spike": ["latency", "scale", "SLO"],
        "bad_deploy_errors": ["deploy", "rollback", "5xx"],
        "disk_pressure": ["disk", "rotate", "log"],
        "cert_expiry": ["cert", "TLS", "renew"],
        "memory_leak": ["memory", "leak", "restart"],
        "db_pool_exhaustion": ["DB", "pool", "scale"],
        "node_not_ready": ["node", "drain", "NotReady"],
        "consumer_lag": ["lag", "consumer", "scale"],
        "dns_failure": ["DNS", "resolve", "restart"],
        "upstream_5xx": ["upstream", "failover", "5xx"],
        "cpu_saturation": ["CPU", "throttle", "scale"],
        "stuck_rollout": ["rollout", "stuck", "rollback"],
        "cache_stampede": ["cache", "hit", "clear"],
    }
    thought_action_aligned = True
    for s in steps:
        if s.role != "assistant" or not s.thought:
            continue
        if s.tool == "end_incident":
            continue
        kws = keywords.get(inc["type"], [])
        if kws and not any(k.lower() in s.thought.lower() for k in kws):
            thought_action_aligned = False
            break

    process_quality = sum([diagnosed_first, args_match, thought_action_aligned]) / 3

    return {
        "incident_type": inc["type"],
        "service": inc["service"],
        "fix_tool": fix_name,
        "canonical_fix": canonical_fix,
        "resolved": resolved,
        "action_correct": action_correct,
        "guardrail_ok": guardrail_ok,
        "reward": reward,
        # process
        "diagnosed_first": diagnosed_first,
        "args_match": args_match,
        "thought_action_aligned": thought_action_aligned,
        "process_quality": round(process_quality, 3),
        # cost
        "n_steps": len(steps),
        "total_tokens": trace.total_input_tokens + trace.total_output_tokens,
        "latency_ms": trace.total_latency_ms,
    }


def aggregate(reports: Iterable[dict]) -> dict:
    reports = list(reports)
    if not reports:
        return {}
    agg = Counter()
    process_aggs = []
    token_totals, step_totals, latency_totals = [], [], []
    by_type = {}
    for r in reports:
        for k in ("resolved", "action_correct", "guardrail_ok", "reward"):
            agg[k] += int(r[k])
        process_aggs.append(r["process_quality"])
        token_totals.append(r["total_tokens"])
        step_totals.append(r["n_steps"])
        latency_totals.append(r["latency_ms"])
        d = by_type.setdefault(r["incident_type"], {"n": 0, "resolved": 0, "reward": 0})
        d["n"] += 1
        d["resolved"] += int(r["resolved"])
        d["reward"] += int(r["reward"])
    n = len(reports)
    return {
        "n": n,
        "resolved_rate": round(agg["resolved"] / n, 4),
        "action_correct_rate": round(agg["action_correct"] / n, 4),
        "guardrail_ok_rate": round(agg["guardrail_ok"] / n, 4),
        "reward_rate": round(agg["reward"] / n, 4),
        "process_quality_mean": round(sum(process_aggs) / n, 4),
        "tokens_mean": round(sum(token_totals) / n, 1),
        "steps_mean": round(sum(step_totals) / n, 2),
        "latency_ms_mean": round(sum(latency_totals) / n, 1),
        "by_incident_type": {
            t: {**d, "resolved_rate": round(d["resolved"] / d["n"], 4),
                "reward_rate": round(d["reward"] / d["n"], 4)}
            for t, d in sorted(by_type.items())
        },
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("traces", nargs="+", help="RunTrace JSON files")
    ap.add_argument("--out", default=None, help="write per-trace reports here")
    args = ap.parse_args()

    all_reports = []
    for path in args.traces:
        with open(path) as f:
            raw = json.load(f)
        trace = RunTrace(**{k: v for k, v in raw.items() if k != "steps"})
        trace.steps = [Step(**s) for s in raw["steps"]]
        r = verify_trace(trace)
        r["trace_file"] = path
        all_reports.append(r)
        print(f"  {path:60s}  reward={r['reward']}  resolved={r['resolved']}  "
              f"fix={r['fix_tool']} (canonical={r['canonical_fix']})  "
              f"process={r['process_quality']}")

    print()
    print("=== AGGREGATE ===")
    agg = aggregate(all_reports)
    for k, v in agg.items():
        if k == "by_incident_type":
            print(f"  by_incident_type:")
            for t, d in v.items():
                print(f"    {t:22s}  n={d['n']:3d}  resolved={d['resolved_rate']:.0%}  reward={d['reward_rate']:.0%}")
        else:
            print(f"  {k:24s}  {v}")

    if args.out:
        Path(args.out).write_text(json.dumps({"reports": all_reports, "aggregate": agg}, indent=2))
        print(f"wrote → {args.out}")


if __name__ == "__main__":
    main()
