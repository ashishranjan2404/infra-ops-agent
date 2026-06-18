"""Agent runtime — the reasoning loop.

Drives an LLM through a K8s incident:
    observe → think → tool → observe → think → tool → ... → end_incident
At every step:
  - the system prompt, the incident (user message), and the running tool-result log
    are sent to the LLM
  - the LLM responds with "Thought: ... Action: tool({...})"
  - the tool is dispatched against the simulator (or, in production, against k8s)
  - the verifier grades the final state

This is the harness that the SFT/DPO checkpoints will plug into.
"""
from __future__ import annotations
import json, time, argparse, os, sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Callable

# Local imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from sim.cluster import ClusterSim, Incident, ToolResult
from agent.llm import (
    LLMMessage, parse_response,
    SYSTEM_PROMPT as AGENT_SYSTEM_PROMPT, stub_plan,
)
import agent.llm as _llm_mod  # so tests/run_e2e can monkey-patch llm_call
import os as _os
_INFRA_AGENT = _os.environ.get(
    "INFRA_AGENT_PATH",
    str(Path(__file__).resolve().parents[2] / "ashish-life-os" / "hackathons" / "inference-time" / "infra-agent"),
)
if _INFRA_AGENT not in sys.path:
    sys.path.insert(0, _INFRA_AGENT)
from generate import INCIDENTS, TRUST  # type: ignore  # noqa: E402


@dataclass
class Step:
    step: int
    role: str                       # "assistant" | "tool"
    thought: str
    tool: str
    args: dict
    trust_tier: str = "autonomous"
    approval: str = "auto"
    tool_result: dict | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    raw_response: str = ""
    error: str | None = None

    def to_dict(self):
        return asdict(self)


@dataclass
class RunTrace:
    incident: dict
    steps: list[Step] = field(default_factory=list)
    final: dict | None = None
    resolved: bool = False
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    total_latency_ms: int = 0
    started_at: float = 0.0
    finished_at: float = 0.0

    def to_dict(self):
        return {
            "incident": self.incident,
            "steps": [s.to_dict() for s in self.steps],
            "final": self.final,
            "resolved": self.resolved,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_latency_ms": self.total_latency_ms,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "duration_s": round(self.finished_at - self.started_at, 3),
        }


# --------------------------------------------------------------------------------
# The harness
# --------------------------------------------------------------------------------

class AgentRuntime:
    def __init__(self, sim: ClusterSim, model: str = "stub",
                 max_steps: int = 8, on_step: Callable | None = None):
        self.sim = sim
        self.model = model
        self.max_steps = max_steps
        self.on_step = on_step    # hook for the website's live-trace UI

    def run(self, incident: Incident) -> RunTrace:
        trace = RunTrace(
            incident=incident.to_dict(),
            started_at=time.time(),
        )
        messages: list[LLMMessage] = [
            LLMMessage("system", AGENT_SYSTEM_PROMPT),
            LLMMessage("user", self._user_message(incident)),
        ]

        for step_idx in range(self.max_steps):
            # Ask the LLM what to do next
            try:
                resp = _llm_mod.llm_call(messages, model=self.model)
            except Exception as e:
                err_step = Step(
                    step=step_idx + 1, role="assistant",
                    thought="", tool="", args={},
                    error=f"llm_call failed: {e}",
                )
                trace.steps.append(err_step)
                if self.on_step: self.on_step(err_step, trace)
                break
            thought, tool, args = parse_response(resp.text)

            trace.total_input_tokens += resp.input_tokens
            trace.total_output_tokens += resp.output_tokens
            trace.total_latency_ms += resp.latency_ms

            # Plan-step record (assistant turn)
            trust = TRUST.get(tool or "", "autonomous")
            step = Step(
                step=step_idx + 1, role="assistant",
                thought=thought or "(no thought)", tool=tool or "", args=args,
                trust_tier=trust,
                input_tokens=resp.input_tokens,
                output_tokens=resp.output_tokens,
                latency_ms=resp.latency_ms,
                raw_response=resp.text,
            )

            # Tool dispatch
            if tool in ("end_incident", None):
                step.tool_result = {"success": True, "notes": "incident closed"}
                trace.steps.append(step)
                if self.on_step: self.on_step(step, trace)
                break
            try:
                result = self.sim.apply_tool(tool, args or {"service_id": incident.service})
            except Exception as e:
                step.error = f"tool dispatch failed: {e}"
                step.tool_result = {"success": False, "error": str(e)}
                trace.steps.append(step)
                if self.on_step: self.on_step(step, trace)
                continue

            step.approval = result.approval
            step.tool_result = {
                "success": result.success, "notes": result.notes,
                "state_diff": result.state_diff,
            }
            trace.steps.append(step)
            if self.on_step: self.on_step(step, trace)

            # Feed the tool result back into the conversation
            messages.append(LLMMessage("assistant", resp.text))
            messages.append(LLMMessage(
                "user",
                f"TOOL_RESULT [{tool}]: {json.dumps({'success': result.success, 'state_diff': result.state_diff, 'notes': result.notes}, default=str)}",
            ))

        # Verifier: did the SLO restore?
        v = self.sim.verify(incident)
        trace.final = v
        trace.resolved = v["resolved"]
        trace.finished_at = time.time()
        return trace

    def _user_message(self, inc: Incident) -> str:
        return (
            "INCIDENT:\n" + json.dumps({
                "incident_type": inc.type,
                "service_id": inc.service,
                "namespace": inc.namespace,
                "alert": inc.alert,
                "severity": inc.severity,
                "incident_context": inc.symptom,
                "primary_metric": inc.metric,
                "bad_value": inc.bad_value,
                "slo_threshold": inc.good_value,
                "direction": inc.direction,
            }, indent=2) + "\n\nResolve it."
        )


# --------------------------------------------------------------------------------
# CLI — run one incident end-to-end and print the trace
# --------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--incident", required=True,
                    help="one of: oom_kill, crashloop, latency_spike, bad_deploy_errors, "
                         "disk_pressure, cert_expiry, memory_leak, db_pool_exhaustion, "
                         "node_not_ready, consumer_lag, dns_failure, upstream_5xx, "
                         "cpu_saturation, stuck_rollout, cache_stampede")
    ap.add_argument("--service", default=None)
    ap.add_argument("--namespace", default="prod")
    ap.add_argument("--model", default="stub")
    ap.add_argument("--max-steps", type=int, default=8)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default=None, help="write the trace JSON here")
    ap.add_argument("--duration", type=float, default=300.0)
    args = ap.parse_args()

    sim = ClusterSim(seed=args.seed, duration_s=args.duration)
    sim.boot()
    inc = sim.inject(args.incident, service=args.service, namespace=args.namespace)
    print(f"[setup] {inc.alert} on {inc.service}/{inc.namespace}  →  bad {inc.metric}={inc.bad_value:.1f}  (SLO {inc.good_value:.1f})")

    rt = AgentRuntime(sim, model=args.model, max_steps=args.max_steps)
    trace = rt.run(inc)

    print()
    print(f"=== REASONING TRACE ({len(trace.steps)} steps) ===")
    for s in trace.steps:
        print(f"  step {s.step}  [{s.role}]  {s.tool or '(no tool)'}")
        if s.thought:
            print(f"      thought: {s.thought[:120]}")
        if s.tool_result:
            print(f"      result : {s.tool_result.get('notes','')[:80]}")
            if s.tool_result.get('state_diff'):
                print(f"      diff   : {s.tool_result['state_diff']}")
    print()
    print(f"=== VERIFIER ===")
    print(f"  before={trace.final['before']:.1f}  after={trace.final['after']:.1f}  "
          f"target={trace.final['target']:.1f}  →  RESOLVED={trace.resolved}  "
          f"(took {trace.final['time_to_resolve_s']}s of sim time)")
    print(f"  tokens: in={trace.total_input_tokens} out={trace.total_output_tokens}  "
          f"latency: {trace.total_latency_ms}ms")

    if args.out:
        Path(args.out).write_text(json.dumps(trace.to_dict(), indent=2, default=str))
        print(f"wrote → {args.out}")


if __name__ == "__main__":
    main()
