#!/usr/bin/env python3
"""
Eval: the demo metric. For a held-out incident slice, ask the model which single
tool resolves the incident and check it against the rules-engine correct fix.
Reports fix-tool accuracy. Run for base, SFT, and DPO models to get the
before -> after numbers (the pitch's headline).

NOTE: this is the single-decision proxy (weekend-demoable). Full agentic rollout
(multi-step tool execution against a simulator) is the stretch goal — wire the
tools to a sim and replay, then grade end-state with verify.py.

  python eval_agent.py --model qwen-infra-dpo --n 1000
"""
import argparse, json, re
import fmt, generate

CORRECT_FIX = {inc["type"]: inc["fix"] for inc in generate.INCIDENTS}
ALL_TOOLS = [n for n, _, _ in generate.TOOLS]


def held_out(n, seed=999):
    import random
    random.seed(seed)
    return [generate.make_trajectory(2_000_000 + i) for i in range(n)]


def parse_tool(text):
    m = re.search(r"Action:\s*([a-z_]+)\s*\(", text) or re.search(r"\b(" + "|".join(ALL_TOOLS) + r")\b", text)
    return m.group(1) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--n", type=int, default=1000)
    args = ap.parse_args()

    from unsloth import FastLanguageModel
    model, tok = FastLanguageModel.from_pretrained(args.model, max_seq_length=4096, load_in_4bit=True, dtype=None)
    FastLanguageModel.for_inference(model)

    correct = 0
    data = held_out(args.n)
    for t in data:
        prompt = [{"role": "system", "content": t["system_prompt"]},
                  {"role": "user", "content": "INCIDENT:\n" + json.dumps(t["user_input"], ensure_ascii=False) +
                   "\n\nReply with the single remediation as: Action: <tool>(<args>)"}]
        ids = tok.apply_chat_template(prompt, add_generation_prompt=True, return_tensors="pt").to(model.device)
        out = model.generate(input_ids=ids, max_new_tokens=64, do_sample=False)
        text = tok.decode(out[0][ids.shape[1]:], skip_special_tokens=True)
        if parse_tool(text) == CORRECT_FIX[t["task_type"]]:
            correct += 1
    print(f"{args.model}: fix-tool accuracy = {correct}/{args.n} ({100*correct/args.n:.1f}%)")


if __name__ == "__main__":
    main()
