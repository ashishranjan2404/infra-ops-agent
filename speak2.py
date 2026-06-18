"""Audio explainer #2: SFT → RLVR → DPO — why each step exists.

Same setup as speak.py — Cartesia sonic-2, Bryce (Clear Explainer), 0.92x speed.
Run with:  python3 /Users/mei/rl/speak2.py --no-play
"""
import os, subprocess, tempfile, json
from pathlib import Path

_HERMES_ENV = Path(os.path.expanduser("~/.hermes/.env"))
if _HERMES_ENV.exists():
    for line in _HERMES_ENV.read_text().splitlines():
        if line.strip().startswith("CARTESIA_API_KEY=") and "=" in line:
            os.environ.setdefault("CARTESIA_API_KEY", line.split("=", 1)[1].strip())

SCRIPT = """
Okay, last time I explained what the SRE agent is. Now let me explain the training, and specifically why we need three separate steps. SFT, then RLVR, then DPO. Each one does a different job, and the order matters.

Let me start with SFT. Supervised Fine Tuning. Here's the problem it solves. Imagine you take a base language model off the shelf, a Qwen, a Llama, whatever. It has read the entire internet. It knows a lot about Kubernetes. It can write code. It can talk about incidents. But it has never seen YOUR format. It doesn't know that your agent has a specific system prompt. It doesn't know that the response has to be "Thought: ... Action: tool name with curly brace args". It doesn't know that there are twenty-five specific tools it can call, and each one has a trust tier, and that drain node is blocked tier so it should escalate. It doesn't know any of the domain specific patterns. Like, the right way to think about an OOM kill versus a crash loop. All of that is novel to the model.

SFT fixes this by showing the model one hundred and fifty thousand examples of an agent doing the job correctly. State, thought, action, tool result, thought, action, all the way to a resolved incident. We feed it trajectories. It adjusts its weights so the next time it sees a similar incident, it produces a response in the right shape. Think of it like teaching someone the moves in chess. Before they play, you sit them down and say, here, watch a hundred thousand games played by good players. Now you know what a knight does. You know the opening patterns. You know the conventions.

So SFT gives the model the format, the tool set, the domain knowledge, the basic shape of good incident response. After SFT, the model can competently handle the incidents it's seen, in the shape we've defined.

But here's the thing. SFT is memorization. The model is learning to imitate the trajectories you showed it. If you show it a hundred thousand OOM kills, it'll be great at OOM kills. But it hasn't really learned to reason about NEW situations, ones you didn't put in the training set. And more importantly, our training data is synthetic. It's templated. The thoughts sound like thoughts, but they're not the kinds of thoughts a real model would actually have. So the model has learned the format, but it hasn't yet learned to win at the actual game.

That's where RLVR comes in. Reinforcement Learning with Verifiable Rewards. This is the GRPO step, the thing Beibei mentioned, the DeepSeek R one technique. Let me explain what it does differently from SFT.

In SFT, you show the model a fixed set of examples and it imitates them. In RLVR, you let the model TRY. You give it an incident it's never seen. It produces a trajectory, a sequence of thought, action, tool result, thought, action. And at the end, the verifier scores it. Resolved or not. That's it. A zero or a one. And then the model updates its weights to make trajectories like the good one more likely, and trajectories like the bad one less likely. The model learns by DOING, not by imitating.

And the key word here is VERIFIABLE. The reward isn't "a human thought this was good". That would be slow, expensive, and inconsistent. The reward is "the metric crossed back under its SLO". That's a deterministic check. You run it a million times, you get the same answer. Did memory drop below sixty-five percent? Yes or no. Did the agent use the right tool? Yes or no. Did it request approval when it needed to? Yes or no. There's no judgment, no LLM in the loop, no fluff. Just a math check.

This is what lets RLVR scale. You can run a million rollouts in a day. The verifier grades them. The model improves. Without the verifiable reward, you'd be bottlenecked on human reviewers or on a second model acting as a judge, which is slow, expensive, and the judge model has its own biases.

So SFT teaches the format. RLVR teaches the OUTCOME. After RLVR, the model can handle new incidents it has never seen, and reliably resolve them, because it's been trained on its own attempts, scored by a ground truth check.

But here's the third gap, and this is where DPO comes in. Even after RLVR, the model can still be doing the right thing for the wrong reason. Watch this.

Two trajectories for the same OOM kill. Trajectory A: the agent describes the pod, reads the metrics, confirms memory is over SLO, then calls increase memory limit with the right arguments. Resolved. Trajectory B: the agent immediately calls increase memory limit without any diagnosis, gets lucky, it still works, resolved. Both trajectories get reward one from the verifier. Both pass. The model thinks they're equally good.

But A is the kind of agent you want. B is fragile. In a real production cluster, an agent that acts without diagnosis is dangerous. It will sometimes pick the right tool by accident, but other times it will escalate incidents, mask root causes, make things worse. The binary verifier can't see that. All it sees is the final state.

So we need a second signal. One that captures PROCESS quality, not just outcome quality. That's DPO. Direct Preference Optimization.

Here's how it works. We collect pairs of trajectories for the same incident. One trajectory is the "winner" — it has the qualities we want. The agent diagnosed first. Its thoughts match its actions. Its arguments are correct. It respected the trust tiers. The other trajectory is the "loser" — maybe it skipped diagnosis. Maybe it hallucinated args. Maybe the thought was nonsense but the action happened to work. Same incident, same outcome, but one is clearly the better way to be an agent.

We feed those pairs to the model during training. The model learns: prefer the shape of the winner, avoid the shape of the loser. The preferences encode things the binary verifier can't see.

So now we have three layers. SFT teaches the format and the domain. RLVR teaches the outcome — make the SLO go green, the verifier will check. DPO teaches the taste — diagnose first, match thoughts to actions, respect guardrails, be the kind of agent a human would trust to run on their cluster at three in the morning.

Without SFT, the model can't even respond in the right format. Without RLVR, the model can't generalize to new incidents. Without DPO, the model resolves incidents but in ugly ways that humans wouldn't trust. Each one is necessary. Each one teaches something the others can't.

That's the three step pipeline. Format, then outcome, then taste. And the whole point of making the reward verifiable is that you can iterate the RLVR step cheaply, at scale, without humans in the loop. The DPO step is where humans contribute, by labeling which trajectory is the better way to be. It's the only step that needs a human, and that's the right place to put the human.

Let me know if any of that was still fuzzy, or if you want me to go deeper on any one of the three.
"""


def synth_cartesia(text: str, out_path: Path, voice_id: str, key: str, speed: float):
    body = {
        "model_id": "sonic-2",
        "transcript": text.strip(),
        "voice": {"mode": "id", "id": voice_id},
        "output_format": {"container": "mp3", "encoding": "mp3", "sample_rate": 44100},
        "voice_controls": {"speed": speed},
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(body, f, ensure_ascii=False)
        payload_path = f.name
    try:
        subprocess.run(
            ["curl", "-sS", "--max-time", "180",
             "-X", "POST",
             "-H", f"Authorization: Bearer {key}",
             "-H", "Cartesia-Version: 2024-06-10",
             "-H", "Content-Type: application/json",
             "--data-binary", f"@{payload_path}",
             "https://api.cartesia.ai/tts/bytes",
             "-o", str(out_path)],
            check=True,
        )
    finally:
        os.unlink(payload_path)
    return out_path


VOICES = {
    "bryce":    ("2948c301-9211-4112-8f36-4c3fc836ef12", "Bryce - Clear Explainer"),
    "sophie":   ("bf0a246a-8642-498a-9950-80c35e9276b5", "Sophie - Teacher"),
    "clara":    ("01eaafa9-308a-4276-a017-6ab0cf061b1f", "Clara - Instructor"),
    "marilyn":  ("f9fc912e-52f0-448a-8bfa-47e9ca75f25a", "Marilyn - Explainer"),
}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="bryce", choices=list(VOICES.keys()))
    ap.add_argument("--speed", type=float, default=0.92)
    ap.add_argument("--no-play", action="store_true")
    args = ap.parse_args()

    voice_id, voice_name = VOICES[args.voice]
    out = Path(f"/Users/mei/rl/sft-rlvr-dpo-{args.voice}.mp3")
    key = os.environ["CARTESIA_API_KEY"]

    print(f"voice: {voice_name}  speed={args.speed}  model=sonic-2")
    synth_cartesia(SCRIPT, out, voice_id, key, args.speed)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")

    if not args.no_play:
        # Audio safety: never play two streams at once.
        running = subprocess.run(["pgrep", "-f", "afplay"],
                                 capture_output=True, text=True).stdout.strip()
        if running:
            print(f"afplay already running (pid {running.split()[0]}) — killing before playback")
            subprocess.run(["pkill", "-9", "afplay"], capture_output=True)
        subprocess.Popen(["afplay", str(out)])
        print(f"(playing in background — `pkill afplay` to stop)")


if __name__ == "__main__":
    main()
