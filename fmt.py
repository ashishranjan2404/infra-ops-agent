#!/usr/bin/env python3
"""Shared formatting: trajectory <-> chat messages, and preference-pair rendering.
Used by train_sft.py / train_dpo.py / eval_agent.py. No heavy deps (pure stdlib)."""
import json


def _action_text(step):
    a = step["action"]
    return f'Thought: {step.get("thought","")}\nAction: {a["tool"]}({json.dumps(a.get("args",{}), ensure_ascii=False)})'


def to_messages(t):
    """A trajectory -> OpenAI-style chat messages (system / user / assistant)."""
    msgs = [{"role": "system", "content": t["system_prompt"]}]
    msgs.append({"role": "user", "content": "INCIDENT:\n" + json.dumps(t["user_input"], ensure_ascii=False)})
    for s in t["trajectory"]:
        if s["role"] == "assistant":
            msgs.append({"role": "assistant", "content": _action_text(s)})
        else:
            msgs.append({"role": "user",
                         "content": f'TOOL_RESULT [{s.get("name","")}]: ' + json.dumps(s.get("content", {}), ensure_ascii=False)})
    return msgs


def _body(t):
    out = []
    for s in t["trajectory"]:
        if s["role"] == "assistant":
            out.append(_action_text(s))
        else:
            out.append(f'TOOL_RESULT [{s.get("name","")}]: ' + json.dumps(s.get("content", {}), ensure_ascii=False))
    return "\n".join(out)


def to_pref(pair):
    """A Path-C pair -> {prompt, chosen, rejected} for TRL DPOTrainer."""
    w, l = pair["winner"], pair["loser"]
    prompt = w["system_prompt"] + "\n\nINCIDENT:\n" + json.dumps(w["user_input"], ensure_ascii=False) + "\n\nResolve it:"
    return {"prompt": prompt, "chosen": "\n" + _body(w), "rejected": "\n" + _body(l)}
