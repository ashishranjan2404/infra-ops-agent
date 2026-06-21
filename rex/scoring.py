"""Phase-1 scoring + feedback.

score_plan -> (score in [0,1], feedback): GRADED, not binary.
  0.30 * root_cause_match  +  0.25 * correct_fix_present  +  0.45 * resolved
  minus a BIG penalty (0.60) if any trap/forbidden action appears.
A perfect, resolved, trap-free plan scores 1.0; a trap drags it far down.

format_feedback -> str: SPECIFIC, actionable text the model climbs on — what the
root cause should have been vs what was given, whether a correct fix tool was
present, whether a trap action appeared and WHY it's wrong, and whether the metric
was restored.
"""
from __future__ import annotations

W_ROOT, W_FIX, W_RESOLVED, TRAP_PENALTY = 0.30, 0.25, 0.45, 0.60


def _applied(plan: dict, sim_result: dict) -> list:
    return sim_result.get("applied_actions", plan.get("actions", []))


def _root_cause_match(plan: dict, scenario) -> float:
    text = (plan.get("root_cause") or "").lower()
    kws = scenario.root_cause_keywords
    if not kws:
        return 0.0
    return sum(1 for k in kws if k.lower() in text) / len(kws)


def _fix_credit(actions: list, scenario) -> float:
    on_target = any(a.get("tool") in scenario.correct_fix_tools
                    and a.get("args", {}).get("target") == scenario.fault_node
                    for a in actions)
    if on_target:
        return 1.0
    right_tool = any(a.get("tool") in scenario.correct_fix_tools for a in actions)
    return 0.5 if right_tool else 0.0


def _traps_in(actions: list, scenario) -> list:
    hits = []
    for a in actions:
        for t in scenario.trap_actions:
            same_target = t.get("target") in (None, a.get("args", {}).get("target"))
            if a.get("tool") == t["tool"] and same_target:
                hits.append(a)
    return hits


def score_plan(plan: dict, scenario, sim_result: dict):
    actions = _applied(plan, sim_result)
    rc = _root_cause_match(plan, scenario)
    fix = _fix_credit(actions, scenario)
    resolved = 1.0 if sim_result.get("resolved") else 0.0
    trap_hit = bool(_traps_in(actions, scenario))

    score = W_ROOT * rc + W_FIX * fix + W_RESOLVED * resolved
    if trap_hit:
        score -= TRAP_PENALTY
    score = max(0.0, min(1.0, score))
    return score, format_feedback(plan, scenario, sim_result)


def format_feedback(plan: dict, scenario, sim_result: dict) -> str:
    actions = _applied(plan, sim_result)
    lines: list[str] = []

    # 1. root cause: what it should have been vs what was given
    rc = _root_cause_match(plan, scenario)
    given = plan.get("root_cause") or "(none given)"
    truth = (f"a {scenario.category} root cause — specifically a per-process memory leak: "
             f"'{scenario.fault_node}' leaks heap until RSS crosses its container memory "
             f"limit and the kernel OOM-kills it (OOMKilled / exit 137).")
    if rc >= 0.6:
        lines.append(f"ROOT CAUSE: correct ({rc:.0%} of the key signals named). It is {truth}")
    else:
        lines.append(f"ROOT CAUSE: your diagnosis '{given}' misses it. The real root cause is {truth}")

    # 2. correct fix tool present?
    fix_tools = ", ".join(sorted(scenario.correct_fix_tools))
    if _fix_credit(actions, scenario) >= 1.0:
        present = sorted({a["tool"] for a in actions if a.get("tool") in scenario.correct_fix_tools})
        lines.append(f"FIX: your plan included a correct fix ({', '.join(present)}) targeting "
                     f"'{scenario.fault_node}'. Good.")
    else:
        lines.append(f"FIX: your plan did NOT include a remediation that addresses a memory leak. "
                     f"What resolves it: give the pod memory headroom and clear the leaked heap "
                     f"(tools: {fix_tools}), targeting '{scenario.fault_node}'.")

    # 3. trap actions + WHY they are wrong
    for a in _traps_in(actions, scenario):
        tool = a.get("tool")
        why = {
            "scale_deployment": "the leak is per-process, so every new replica leaks and OOMs the "
                                "same way — adding replicas will NOT restore SLO and wastes capacity",
            "clear_cache": "clearing a cache does not free leaked heap — the OOM loop continues, so "
                           "it will NOT resolve the incident",
        }.get(tool, "it does not address the root cause, so it will not resolve the incident")
        lines.append(f"TRAP: you used '{tool}' — this is WRONG: {why}.")

    # 4. metric / resolution status
    if sim_result.get("resolved"):
        lines.append("RESULT: the sim reports the incident RESOLVED — SLO restored and the root cause cleared.")
    else:
        lines.append("RESULT: the incident is NOT resolved — the root cause is still active and the SLO "
                     "is still breaching. Revise the plan.")
    return "\n".join(lines)
