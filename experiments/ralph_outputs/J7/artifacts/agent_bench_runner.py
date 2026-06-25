#!/usr/bin/env python3
"""agent_bench_runner.py — point the frozen-LLM agent at the live-cloud bench scenarios.

J7 deliverable (task-namespaced; does NOT edit shared core files).

The gcp-bench / linode-bench loop (stages/06_run_scenario.sh) currently applies a
*hardcoded* runbook fix from registry.json. This runner inserts THE AGENT into that
loop: for each incident it builds an SRE prompt from the CRE rule + symptom, presents
the candidate runbook actions (the union of all registry fixes — a real action space),
and asks the frozen LLM policy (agent.llm) to choose the correct fix. The choice is
scored deterministically against the registry's gold fix. No grading model, no cloud.

Two modes:
  --dry-run   (default) OFFLINE, zero cost: uses agent.llm.build_request (pure, no
              network) to PROVE the prompt + provider wiring assemble for every
              scenario, then scores a deterministic baseline policy (lexical match
              between CRE mitigation text and each candidate action). Proves the
              harness end-to-end with no API key and no cloud.
  --live-agent MODEL   calls agent.llm.call(MODEL, ...) — real LLM action selection.
              Still NO cloud: the chosen kubectl command is recorded, never executed.

Applying the chosen action against a real GKE/LKE cluster is the explicit downstream
step that is BLOCKED (see 07_test_results.md): the temp hackathon GCP account was
deleted, so there is no live cluster to act on, and we must not bill personal accounts.

Usage:
  python3 agent_bench_runner.py --bench gcp                 # dry-run, gcp-bench
  python3 agent_bench_runner.py --bench linode --dry-run
  python3 agent_bench_runner.py --bench gcp --live-agent claude-haiku-4-5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]   # .../rl
sys.path.insert(0, str(REPO))


# ----------------------------- scenario loading -----------------------------

def load_registry(bench: str) -> list[dict]:
    reg = REPO / f"{bench}-bench" / "scenarios" / "registry.json"
    if not reg.exists():
        raise FileNotFoundError(f"no registry for bench={bench}: {reg}")
    data = json.loads(reg.read_text())
    return [s for s in data["scenarios"] if not s.get("skip", False)]


def load_cre_text(bench: str, cre_id: str) -> str:
    """Best-effort plain-text pull of the CRE description/cause/mitigation."""
    p = REPO / f"{bench}-bench" / "scenarios" / cre_id
    if not p.exists():
        return ""
    return p.read_text()


# ----------------------------- prompt assembly ------------------------------

SYSTEM = (
    "You are an on-call SRE. An incident has fired on a Kubernetes cluster. "
    "You are given the incident symptom and a numbered list of candidate runbook "
    "actions. Reply with ONLY the single number of the action that resolves THIS "
    "incident. No prose."
)


def build_action_space(scenarios: list[dict]) -> list[str]:
    """The agent's action space = the set of gold runbook fixes (deduped, ordered)."""
    seen, actions = set(), []
    for s in scenarios:
        fix = s["fix"].strip()
        if fix not in seen:
            seen.add(fix)
            actions.append(fix)
    return actions


def build_prompt(scenario: dict, cre_text: str, actions: list[str]) -> str:
    symptom = scenario.get("log_marker", "") or scenario["incident"]
    cre_excerpt = _cre_excerpt(cre_text)
    lines = [
        f"INCIDENT on service `{scenario['service']}`:",
        f"  symptom: {symptom}",
    ]
    if cre_excerpt:
        lines.append(f"  detail: {cre_excerpt}")
    lines.append("")
    lines.append("Candidate runbook actions:")
    for i, a in enumerate(actions):
        lines.append(f"  {i}. {a}")
    lines.append("")
    lines.append("Which action number resolves this incident? Answer with the number only.")
    return "\n".join(lines)


def _cre_excerpt(cre_text: str) -> str:
    """Pull the description+mitigation bullets from a CRE yaml without full parse."""
    if not cre_text:
        return ""
    bits = []
    for key in ("description", "mitigation"):
        m = re.search(rf"{key}:\s*\|\s*\n((?:\s+.*\n?)+)", cre_text)
        if m:
            body = " ".join(l.strip(" -") for l in m.group(1).splitlines() if l.strip())
            bits.append(body)
    return " ".join(bits)[:300]


# ----------------------------- policies -------------------------------------

def baseline_policy(prompt: str, scenario: dict, actions: list[str]) -> int:
    """Deterministic offline baseline: pick the action whose tokens best overlap the
    incident's service + log marker. Provides a real, reproducible score with no API."""
    target = (scenario["service"] + " " + scenario.get("log_marker", "") + " "
              + scenario["incident"]).lower()
    target_toks = set(re.findall(r"[a-z0-9]+", target))
    best_i, best_score = 0, -1.0
    for i, a in enumerate(actions):
        a_toks = set(re.findall(r"[a-z0-9]+", a.lower()))
        score = len(target_toks & a_toks)
        if score > best_score:
            best_i, best_score = i, score
    return best_i


def llm_policy(prompt: str, model: str) -> tuple[int, str]:
    """Live LLM action selection. Returns (chosen_index, raw_text)."""
    from agent.llm import call  # imported lazily so dry-run needs no key
    raw = call(model, prompt, max_tokens=16, system=SYSTEM)
    m = re.search(r"-?\d+", raw)
    return (int(m.group()) if m else -1), raw


def prove_request_assembles(model: str, prompt: str) -> bool:
    """Offline proof that the agent's provider wiring builds a valid request (no net)."""
    from agent.llm import build_request
    url, headers, payload = build_request(model, prompt, max_tokens=16, system=SYSTEM)
    return bool(url) and isinstance(headers, dict) and "messages" in payload or "prompt" in payload


# ----------------------------- runner ---------------------------------------

def run(bench: str, mode: str, model: str) -> dict:
    scenarios = load_registry(bench)
    actions = build_action_space(scenarios)
    gold_index = {s["incident"]: actions.index(s["fix"].strip()) for s in scenarios}

    rows, correct = [], 0
    for s in scenarios:
        cre_text = load_cre_text(bench, s["cre_id"])
        prompt = build_prompt(s, cre_text, actions)
        gi = gold_index[s["incident"]]

        if mode == "dry-run":
            assembled = prove_request_assembles(model, prompt)
            chosen = baseline_policy(prompt, s, actions)
            raw = f"baseline->{chosen}"
        else:
            assembled = True
            chosen, raw = llm_policy(prompt, model)

        ok = (chosen == gi)
        correct += int(ok)
        rows.append({
            "scenario": s["incident"],
            "service": s["service"],
            "gold_action_index": gi,
            "chosen_action_index": chosen,
            "correct": ok,
            "request_assembled": assembled,
            "raw": raw[:80],
            # downstream cloud apply is BLOCKED — recorded, never executed:
            "chosen_action_cmd": actions[chosen] if 0 <= chosen < len(actions) else None,
            "cloud_applied": False,
            "cloud_blocked_reason": "temp GCP account deleted; no live cluster",
        })

    n = len(scenarios)
    return {
        "bench": bench,
        "mode": mode,
        "model": model,
        "n": n,
        "n_actions": len(actions),
        "correct": correct,
        "action_select_accuracy": round(correct / n, 3) if n else 0.0,
        "cloud_executed": False,
        "rows": rows,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bench", choices=["gcp", "linode"], default="gcp")
    ap.add_argument("--dry-run", action="store_true", help="offline, no API, no cost (default)")
    ap.add_argument("--live-agent", metavar="MODEL", default=None,
                    help="call the real LLM policy (e.g. claude-haiku-4-5); still no cloud")
    ap.add_argument("--out", default=None, help="write result json here")
    args = ap.parse_args()

    if args.live_agent:
        mode, model = "live-agent", args.live_agent
    else:
        mode, model = "dry-run", "claude-haiku-4-5"   # model only used to prove wiring

    result = run(args.bench, mode, model)
    text = json.dumps(result, indent=2)
    if args.out:
        Path(args.out).write_text(text)
    print(text)
    print(f"\n{args.bench}-bench [{mode}]: action-select accuracy "
          f"{result['correct']}/{result['n']} = {result['action_select_accuracy']}  "
          f"(cloud_executed={result['cloud_executed']})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
