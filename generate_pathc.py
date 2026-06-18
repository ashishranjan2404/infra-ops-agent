#!/usr/bin/env python3
"""
Path C — failure trajectories (with failure_mode) + winner/loser preference pairs
for DPO. Same schema convention as FIREBALL's docs/schema.md Path C.

Two failure families:
  OUTCOME failures (the verifier catches these): wrong_tool, premature_end,
    unsafe_autonomous_action, tool_call_loop.
  PROCESS failures (still resolve, but worse trajectory — caught by the preference
    model, not the binary verifier): skipped_diagnosis, arg_hallucination,
    thought_action_mismatch.

Usage:
  python generate_pathc.py --rej 20000 --pairs 30000
"""
from __future__ import annotations
import argparse, copy, json, random
import generate

OUTCOME = ["wrong_tool", "premature_end", "unsafe_autonomous_action", "tool_call_loop"]
PROCESS = ["skipped_diagnosis", "arg_hallucination", "thought_action_mismatch"]
PENALTY = {"wrong_tool": 0.65, "premature_end": 0.6, "unsafe_autonomous_action": 0.7,
           "tool_call_loop": 0.55, "skipped_diagnosis": 0.3, "arg_hallucination": 0.35,
           "thought_action_mismatch": 0.4}

REMEDIATION = [n for n, t, _ in generate.TOOLS if t in ("approval", "blocked") or n in
               ("restart_pod", "clear_cache", "rotate_logs")]


def renumber(steps):
    for i, s in enumerate(steps, 1):
        s["step"] = i
    return steps


def _fix_idx(steps, fix_tool):
    for i, s in enumerate(steps):
        if s["role"] == "assistant" and s["action"]["tool"] == fix_tool:
            return i
    return None


def corrupt(base: dict, mode: str) -> dict:
    t = copy.deepcopy(base)
    steps = t["trajectory"]
    fix_tool = t["meta"]["fix_tool"]
    fi = _fix_idx(steps, fix_tool)
    fail_step = fi + 1 if fi is not None else 1

    if mode == "wrong_tool":
        wrong = random.choice([r for r in REMEDIATION if r != fix_tool])
        steps[fi]["action"]["tool"] = wrong
        # the tool result no longer resolves: drop the resolving state_diff
        steps[fi + 1]["name"] = wrong
        steps[fi + 1]["content"] = {"success": True, "note": "no effect on the firing metric"}
        t["meta"]["outcome_correct"] = False

    elif mode == "premature_end":
        # remove the fix assistant+tool steps -> ends without resolving
        del steps[fi:fi + 2]
        t["meta"]["outcome_correct"] = False

    elif mode == "unsafe_autonomous_action":
        # executed a guarded tool WITHOUT approval (guardrail violation)
        steps[fi + 1]["content"]["approval"] = "auto"
        steps[fi]["action"]["requires_approval"] = False

    elif mode == "tool_call_loop":
        d = steps[0]  # first diagnostic
        dt = steps[1]
        loop = []
        for _ in range(4):
            loop.append(copy.deepcopy(d)); loop.append(copy.deepcopy(dt))
        loop.append(steps[-1])  # end_incident, never fixed
        t["trajectory"] = loop
        t["meta"]["outcome_correct"] = False

    elif mode == "skipped_diagnosis":
        # jump straight to the fix (drop the 2 diagnostics) — resolves but reckless
        t["trajectory"] = steps[fi:]

    elif mode == "arg_hallucination":
        steps[fi]["action"]["args"]["service_id"] = random.choice(
            [s for s in generate.SERVICES if s != base["user_input"]["service_id"]])

    elif mode == "thought_action_mismatch":
        other = random.choice([i for i in generate.INCIDENTS if i["type"] != t["task_type"]])
        steps[fi]["thought"] = f"This looks like {other['type']}: {other['symptom']}."

    renumber(t["trajectory"])
    t["meta"]["failure_mode"] = mode
    t["meta"]["failure_step"] = fail_step
    t["meta"]["construction_path"] = "synthetic_corrupted"
    return t


def base_for(i, mode):
    # unsafe_autonomous needs a non-autonomous fix tool
    for _ in range(20):
        b = generate.make_trajectory(i)
        if mode != "unsafe_autonomous_action" or generate.TRUST[b["meta"]["fix_tool"]] != "autonomous":
            return b
    return b


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rej", type=int, default=20000)
    ap.add_argument("--pairs", type=int, default=30000)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)
    modes = OUTCOME + PROCESS

    with open("rejections.jsonl", "w") as f:
        for i in range(args.rej):
            mode = random.choice(modes)
            base = base_for(900000 + i, mode)
            bad = corrupt(base, mode)
            f.write(json.dumps({
                "rejection_id": f"rej_{i:06d}",
                "seed_input_id": base["seed_input_id"],
                "failure_mode": mode,
                "failure_step": bad["meta"]["failure_step"],
                "trajectory": bad,
                "meta": {"auto_labeled": True, "task_type": base["task_type"]},
            }) + "\n")

    with open("pairs.jsonl", "w") as f:
        for i in range(args.pairs):
            mode = random.choice(modes)
            winner = base_for(800000 + i, mode)
            loser = corrupt(winner, mode)
            wscore, lscore = 1.0, round(1.0 - PENALTY[mode] * random.uniform(0.8, 1.0), 2)
            f.write(json.dumps({
                "pair_id": f"pair_{i:06d}",
                "seed_input_id": winner["seed_input_id"],
                "task_type": winner["task_type"],
                "difficulty": winner["difficulty"],
                "score_diff": round(wscore - lscore, 2),
                "loser_failure_mode": mode,
                "winner": winner,
                "loser": loser,
            }) + "\n")

    print(f"wrote rejections.jsonl ({args.rej}) + pairs.jsonl ({args.pairs})")
    print(f"failure modes: outcome={OUTCOME} process={PROCESS}")


if __name__ == "__main__":
    main()
