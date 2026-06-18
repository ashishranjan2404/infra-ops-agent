"""LLM client — supports a *stub* (deterministic, no API key) and Anthropic API.

The stub is the default so the website demo and end-to-end smoke test work anywhere.
Swap in the real Anthropic client by setting ANTHROPIC_API_KEY — the prompt format
is identical so the rest of the agent loop doesn't change.

Why a stub?  Three reasons:
  1. The website needs to show a full reasoning trace deterministically (no jitter).
  2. The agent harness is what's being demoed; the LLM is interchangeable.
  3. The dataset `incidents_seed.jsonl` already encodes the "ground-truth" reasoning
     for every (service, incident_type) pair — we replay those when no LLM is wired.
"""
from __future__ import annotations
import os, json, re, random, time
from dataclasses import dataclass, field
from typing import Optional

# Try Anthropic (preferred); fall back to stub silently.
try:
    import anthropic
    _HAS_ANTHROPIC = True
except ImportError:
    _HAS_ANTHROPIC = False


@dataclass
class LLMMessage:
    role: str   # "system" | "user" | "assistant"
    content: str


@dataclass
class LLMResponse:
    text: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    raw: dict = field(default_factory=dict)


# --------------------------------------------------------------------------------
# Stub: deterministic "ground-truth" reasoning for every incident in our taxonomy.
# The chain-of-thought matches the FIREBALL-style trajectories in
# infra-agent/incidents_seed.jsonl — same thought templates, same tool sequence.
# --------------------------------------------------------------------------------

THOUGHT_ASSESS = [
    "Alert {alert} firing on {service} in {namespace}. {symptom}. Pull metrics before acting.",
    "{service} is paging: {symptom}. First confirm scope by reading {tool}.",
    "Looks like {symptom} on {service}. Don't act blind — pull {tool} to confirm.",
    "{alert} on {service}/{namespace}. Verify {metric} rather than assume the cause.",
]
THOUGHT_SECOND = [
    "{metric} is at {value} — well outside the SLO of {slo}. One more signal from {tool} to be sure.",
    "Confirmed degradation ({metric}={value}). Checking {tool} to pin the cause.",
    "That matches the symptom. {tool} should give me corroborating evidence.",
]
THOUGHT_FIX = [
    "Root cause matches {type}. The correct remediation is {fix}. {gate}",
    "Given the evidence, {fix} is the right fix for {type}. {gate}",
    "This is a textbook {type}. Applying {fix}. {gate}",
]
THOUGHT_END = [
    "{metric} recovered to {value} — within SLO ({slo}). Incident resolved.",
    "Remediation worked: {metric}={value}. Closing out.",
    "System healthy again ({metric}={value}). Ending the incident.",
]
GATE = {
    "autonomous": "This tool is autonomous — executing.",
    "approval": "This tool needs human approval — requesting it.",
    "blocked": "This tool is guarded — escalating.",
}

import sys
from pathlib import Path
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_INFRA_AGENT = os.environ.get(
    "INFRA_AGENT_PATH",
    str(_PROJECT_ROOT.parent / "ashish-life-os" / "hackathons" / "inference-time" / "infra-agent"),
)
if _INFRA_AGENT not in sys.path:
    sys.path.insert(0, _INFRA_AGENT)
from generate import INCIDENTS, SERVICES, TRUST  # type: ignore  # noqa: E402


def stub_thought(phase: str, **kw) -> str:
    if phase == "assess":
        return random.choice(THOUGHT_ASSESS).format(**kw)
    if phase == "second":
        return random.choice(THOUGHT_SECOND).format(**kw)
    if phase == "fix":
        kw["gate"] = GATE.get(TRUST.get(kw["fix"], "autonomous"), GATE["autonomous"])
        return random.choice(THOUGHT_FIX).format(**kw)
    if phase == "end":
        return random.choice(THOUGHT_END).format(**kw)
    return ""


def stub_plan(incident: dict, available_tools: list[str], rng: random.Random) -> list[dict]:
    """Return the canonical 7-step trajectory for an incident: 2 diagnostics → fix → end.

    This is the SAME shape as the FIREBALL trajectories in incidents_seed.jsonl —
    so the verifier, the trust-tier accounting, and the DPO pairs all line up.
    """
    typ = incident["type"]
    inc_def = next(i for i in INCIDENTS if i["type"] == typ)
    fix_tool = inc_def["fix"]
    d1, d2 = inc_def["diag"]
    svc, ns = incident["service"], incident["namespace"]
    metric = inc_def["metric"]
    bad = incident["bad_value"]
    slo = incident["slo_threshold"]
    tier = TRUST.get(fix_tool, "autonomous")

    steps = []

    # Diagnostic 1 (always)
    steps.append({
        "phase": "assess",
        "thought": stub_thought("assess", alert=incident["alert"], service=svc,
                                 namespace=ns, symptom=incident["symptom"], tool=d1, metric=metric),
        "tool": d1, "args": {"service_id": svc, "namespace": ns},
    })

    # Diagnostic 2
    steps.append({
        "phase": "second",
        "thought": stub_thought("second", metric=metric, value=bad, slo=slo, tool=d2),
        "tool": d2, "args": {"service_id": svc, "namespace": ns},
    })

    # Fix
    fix_args = {"service_id": svc, "namespace": ns}
    if fix_tool == "scale_deployment":
        fix_args["replicas"] = 5
    if fix_tool == "scale_consumers":
        fix_args["target_replicas"] = 6
    if fix_tool == "increase_memory_limit":
        fix_args["new_limit_mb"] = 1024
    steps.append({
        "phase": "fix",
        "thought": stub_thought("fix", type=typ, fix=fix_tool),
        "tool": fix_tool, "args": fix_args,
        "trust_tier": tier,
    })

    # End
    steps.append({
        "phase": "end",
        "thought": stub_thought("end", metric=metric, value=slo, slo=slo),
        "tool": "end_incident", "args": {"service_id": svc},
    })
    return steps


# --------------------------------------------------------------------------------
# Claude API client (when ANTHROPIC_API_KEY is set)
# --------------------------------------------------------------------------------

SYSTEM_PROMPT = (
    "You are a platform-engineering (SRE) agent on call. An incident is firing. "
    "Assess the system state by reading metrics/logs/events, then decide and execute "
    "remediation using the available tools. Respect tool guardrails (some actions need "
    "human approval). End with end_incident once the SLO is restored.\n\n"
    "Reply in EXACTLY this format per turn:\n"
    "Thought: <one-sentence chain-of-thought>\n"
    "Action: <tool_name>(<json_args>)\n"
)


def call_anthropic(messages: list[LLMMessage], model: str = "claude-sonnet-4-5",
                   max_tokens: int = 256, temperature: float = 0.2) -> LLMResponse:
    """Call the Anthropic API. Returns a structured LLMResponse."""
    assert _HAS_ANTHROPIC, "pip install anthropic"
    api_key = os.environ["ANTHROPIC_API_KEY"]
    client = anthropic.Anthropic(api_key=api_key)
    system = next((m.content for m in messages if m.role == "system"), SYSTEM_PROMPT)
    chat = [{"role": m.role, "content": m.content}
            for m in messages if m.role in ("user", "assistant")]
    t0 = time.time()
    msg = client.messages.create(
        model=model, system=system, messages=chat,
        max_tokens=max_tokens, temperature=temperature,
    )
    latency_ms = int((time.time() - t0) * 1000)
    text = msg.content[0].text if msg.content else ""
    return LLMResponse(
        text=text, model=model,
        input_tokens=msg.usage.input_tokens,
        output_tokens=msg.usage.output_tokens,
        latency_ms=latency_ms,
        raw={"stop_reason": msg.stop_reason, "id": msg.id},
    )


# --------------------------------------------------------------------------------
# Parse "Thought: ... \n Action: tool(args)" from any LLM output
# --------------------------------------------------------------------------------

ACTION_RE = re.compile(r"Action:\s*([a-z_]+)\s*\(\s*(\{.*?\})\s*\)", re.DOTALL)


def parse_response(text: str) -> tuple[str, Optional[str], dict]:
    """Extract (thought, tool_name, args) from an LLM response.
    Falls back to None tool if it can't parse.
    """
    thought = ""
    m = re.search(r"Thought:\s*(.+?)(?:\n\s*Action:|$)", text, re.DOTALL)
    if m:
        thought = m.group(1).strip()
    m = ACTION_RE.search(text)
    if m:
        tool_name = m.group(1)
        try:
            args = json.loads(m.group(2))
        except json.JSONDecodeError:
            args = {}
        return thought, tool_name, args
    return thought, None, {}


# --------------------------------------------------------------------------------
# The two entry points the agent runtime uses
# --------------------------------------------------------------------------------

def llm_call(messages: list[LLMMessage], model: str = "stub",
             temperature: float = 0.0) -> LLMResponse:
    """Dispatch to either the stub or the Anthropic API based on env / model name."""
    if model == "stub" or not os.environ.get("ANTHROPIC_API_KEY"):
        return _stub_call(messages, temperature)
    return call_anthropic(messages, model=model, temperature=temperature)


def _stub_call(messages: list[LLMMessage], temperature: float) -> LLMResponse:
    """The stub 'LLM' produces a structured response that mirrors what Claude would
    output for the same incident. Used for the website demo and offline replay.

    The stub uses the INCIDENT message (the first user turn), not the most recent
    tool-result message, to drive its plan — so it stays correct across multi-step
    runs regardless of how many tool calls have happened.
    """
    # Find the original incident message (first user turn that contains "INCIDENT:")
    inc_msg = next((m for m in messages if m.role == "user" and "INCIDENT:" in m.content), None)
    if not inc_msg:
        return LLMResponse(text="Thought: nothing to do.\nAction: end_incident({})",
                            model="stub", input_tokens=0, output_tokens=12, latency_ms=1)
    try:
        payload = json.loads(inc_msg.content.split("INCIDENT:\n", 1)[1].split("\n\nResolve")[0])
    except Exception:
        payload = {}
    inc_type = payload.get("incident_type", "oom_kill")
    svc = payload.get("service_id", "checkout")
    ns = payload.get("namespace", "prod")
    # Count tool-result messages to decide which step we're on
    tool_results_so_far = sum(1 for m in messages if m.role == "user" and "TOOL_RESULT" in m.content)
    rng = random.Random((hash(inc_msg.content) ^ tool_results_so_far) & 0xFFFFFFFF)
    steps = stub_plan({
        "type": inc_type,
        "service": svc,
        "namespace": ns,
        "alert": payload.get("alert", "AlertFiring"),
        "symptom": payload.get("incident_context", "anomaly detected"),
        "metric": payload.get("primary_metric", "p99_latency_ms"),
        "bad_value": payload.get("bad_value", 1000),
        "slo_threshold": payload.get("slo_threshold", 200),
    }, [], rng)

    # Pick the next step the agent should take
    step = steps[min(tool_results_so_far, len(steps) - 1)]
    text = f"Thought: {step['thought']}\nAction: {step['tool']}({json.dumps(step['args'])})"
    return LLMResponse(
        text=text, model="stub-deterministic",
        input_tokens=len(inc_msg.content) // 4,
        output_tokens=len(text) // 4,
        latency_ms=2,
    )
