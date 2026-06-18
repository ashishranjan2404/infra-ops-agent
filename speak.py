"""Convert the project explainer to a slow, well-paced audio file.

Uses Cartesia TTS (high quality, low latency). Set CARTESIA_API_KEY in
~/.hermes/.env (already stored). Falls back to macOS `say` if Cartesia fails.
"""
import os, sys, subprocess, urllib.request, json
from pathlib import Path

# Try loading from Hermes .env first (already set up)
_HERMES_ENV = Path(os.path.expanduser("~/.hermes/.env"))
if _HERMES_ENV.exists():
    for line in _HERMES_ENV.read_text().splitlines():
        if line.strip().startswith("CARTESIA_API_KEY=") and "=" in line:
            os.environ.setdefault("CARTESIA_API_KEY", line.split("=", 1)[1].strip())

# The explanation, rewritten as a single flowing monologue so it sounds
# natural when spoken (no bullets, no "section one, section two").
SCRIPT = """
Okay, let me walk you through what I actually built, in plain language. No jargon for jargon's sake.

The big idea is this. I built a small SRE agent, that's a Site Reliability Engineering agent. It's an on-call engineer that lives inside a Kubernetes cluster. When something breaks, an alert fires, the agent reads the state of the system, thinks about it, and then takes an action to fix it.

Now, the actual things I wrote live in five folders. Let me describe what each one does.

The first folder is called sim. That stands for simulator. It's a fake Kubernetes cluster. Sixteen services, fifteen types of things that can go wrong. So I can inject an incident, like "this service is leaking memory", and the cluster responds exactly the way a real one would. The metric, the number you'd see on a dashboard, ramps up to a bad value. Then when the agent applies a fix, the metric drops back down to healthy. It's the world the agent lives in.

The second folder is agent. That's the reasoning harness. It works like a conversation. First, the system gives the agent a system prompt that explains its job. Then the user message describes the incident. The agent thinks, then it speaks. The agent's response has a specific shape. First, a thought, like "the memory is way over the SLO, I need to investigate". Then an action, like "get metrics on the cart service". I parse that out, run the tool against the simulator, take the result, and feed it back in. The agent thinks again, takes another action, and eventually declares the incident over.

The third folder is verify. That's the grader. After the agent runs, the verifier checks three things. Did the affected metric cross back under its Service Level Objective, that's the agreed-upon healthy threshold? Did the agent pick the right tool for the job? And, if the tool needed a human's approval, did the agent request that approval? Combine all three and you get a binary reward. One if everything went right, zero if anything went wrong. This is what makes the training data useful. It's not some fluffy "I thought it was good" judgment. It's a deterministic check. You can run it a million times and get the same answer.

The fourth folder is metrics. That's the data recorder. Every run writes out a per-service metrics file in the exact same shape as a real benchmark called RCAEval. Same column count, same time-series layout, same inject timestamp file. So our offline training data and any live cluster data can be graded by the same verifier, no glue code required.

And finally there's run e two e, the end to end runner. You tell it how many scenarios to run, and which model to use. It walks through each one, injects the incident, runs the agent, scores the result, and saves everything. The default model is a deterministic stub that replays the canonical reasoning plan from the dataset. If you set an Anthropic API key, it'll call Claude instead. The two are interchangeable, the rest of the harness doesn't care.

Now, you asked me to explain what trajectory data means. Here's the simplest way I can put it.

A trajectory is one complete recorded attempt by the agent to solve one incident. Think of it like a game replay. You know how in chess, you can rewind and see every single move? A trajectory is that, but for an SRE agent fixing an alert.

It captures the whole chain. The state of the system when the incident started. The first thing the agent thought. The first tool it called and the arguments it passed. What the tool returned. The agent's second thought. The second tool. And so on, until either the agent says the incident is resolved, or it gives up. Every step is timestamped and recorded.

For example, here's a real one from the dataset. The cart service is in production. Memory utilization is at ninety-eight percent. There's a Pod OOM Killed alert firing. The agent thinks "this looks like an out-of-memory kill, let me describe the pod to see what's going on". It calls describe pod. The tool says the pod has a five hundred and twelve megabyte memory limit and has restarted three times. The agent thinks "confirmed, memory is way over the SLO of sixty-five percent, this is a textbook OOM kill". It calls increase memory limit, raising the limit to one gigabyte. The metric drops. The agent thinks "memory is back to a healthy level, incident resolved". It calls end incident. And the verifier checks, yes, memory is at sixty-five percent, the SLO is met, reward is one.

That whole chain, from the initial alert to the final end incident call, is one trajectory.

And we have one hundred and fifty thousand of them in the training set. Each one is an example of the agent doing the right thing. The model learns the pattern, the format, the right tool for the right situation.

There's also a second dataset of preference pairs. Thirty thousand of them. For each pair, you have a good trajectory and a bad trajectory for the same incident. The bad one might use the wrong tool, or skip the diagnostic step, or hallucinate arguments. The model learns to prefer the good one. That's the DPO step, Direct Preference Optimization. It teaches the agent that process matters, not just outcomes.

Why do you need both? Because here's the subtle thing. The binary verifier, the one that gives you a one or a zero, can't tell the difference between two trajectories that both resolve. If the agent uses the right tool and the metric recovers, reward is one, full stop. Even if the agent skipped the diagnostic step, even if the thought was nonsense, even if the args were wrong but happened to still work. The verifier can't see any of that. It only looks at the final state.

But you want an agent that diagnoses before acting. You want one whose thoughts actually match its actions. You want one that hallucinates less. The binary reward alone can't teach that. The preference pairs can. They say "these two trajectories both resolve, but the first one is the kind of agent you want to be".

So SFT teaches the format. DPO teaches the taste. The binary reward drives both, and the preference data fills in the gaps that the binary reward can't see.

That's the whole story. End to end. Sim to agent to verifier to metrics, all wired together, runs in a few seconds, and produces the data you need to actually train the model.

Let me know if any piece is still fuzzy. I'd rather explain it twice than have you nodding along without getting it.
"""


def find_good_voice(key: str) -> tuple[str, str]:
    """Find a high-quality English voice suited to explanation/narration."""
    req = urllib.request.Request(
        "https://api.cartesia.ai/voices",
        headers={"Authorization": f"Bearer {key}", "Cartesia-Version": "2024-06-10"},
    )
    data = json.loads(urllib.request.urlopen(req, timeout=10).read())
    # Prefer: English + "explainer" / "guide" / "narrator" / "warm" / "calm"
    preferred_keywords = ["explainer", "narrator", "guide", "calm", "warm", "storyteller", "gentle", "soft", "news"]
    candidates = [v for v in data if v.get("language", "").startswith("en")]
    for kw in preferred_keywords:
        for v in candidates:
            name = (v.get("name") or "").lower()
            desc = (v.get("description") or "").lower()
            if kw in name or kw in desc:
                return v["id"], f"{v['name']} ({kw})"
    # Fall back to first English voice
    if candidates:
        return candidates[0]["id"], f"{candidates[0]['name']} (first english)"
    raise RuntimeError("no English voices found")


def synth_cartesia(text: str, out_path: Path, voice_id: str, key: str,
                   speed: float = 0.92) -> Path:
    """Synthesize via Cartesia Sonic-2 TTS. Returns path to audio file.

    Speed < 1.0 is slower.  We use curl (not urllib) because Python's
    bundled SSL on this system doesn't trust the Cartesia cert chain
    (curl has its own cert store and works fine).

    Cartesia returns the audio bytes directly when the request is
    well-formed, so we can write the response body straight to disk.
    """
    body = {
        # sonic-2 is Cartesia's latest English model — noticeably more natural
        # than sonic-english, especially for slow, conversational narration.
        "model_id": "sonic-2",
        "transcript": text.strip(),
        "voice": {"mode": "id", "id": voice_id},
        "output_format": {
            "container": "mp3",
            "encoding": "mp3",
            "sample_rate": 44100,
        },
        # Speed < 1.0 slows the audio. 0.92 reads at a measured, teacher
        # pace — slower than 1.0 but not so slow it sounds sluggish.
        "voice_controls": {"speed": speed},
    }
    # Write the JSON payload to a temp file so the shell doesn't have to
    # worry about quoting (the script is multi-kB).
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(body, f, ensure_ascii=False)
        payload_path = f.name
    try:
        subprocess.run(
            ["curl", "-sS", "--max-time", "120",
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


def synth_macos_say(text: str, out_path: Path) -> Path:
    """Fallback: macOS `say` → AIFF → MP3 via ffmpeg."""
    aiff = out_path.with_suffix(".aiff")
    subprocess.run(["say", "-v", "Samantha", "-r", "165", "-o", str(aiff), text], check=True)
    subprocess.run(["ffmpeg", "-y", "-i", str(aiff), str(out_path)],
                   check=True, capture_output=True)
    aiff.unlink(missing_ok=True)
    return out_path


# Voice choices — "explainer / teacher" tone.
# Use --voice NAME to override at the CLI; default is the literal "Clear Explainer".
VOICES = {
    "bryce":   ("2948c301-9211-4112-8f36-4c3fc836ef12", "Bryce - Clear Explainer"),
    "sophie":  ("bf0a246a-8642-498a-9950-80c35e9276b5", "Sophie - Teacher"),
    "clara":   ("01eaafa9-308a-4276-a017-6ab0cf061b1f", "Clara - Instructor"),
    "marilyn": ("f9fc912e-52f0-448a-8bfa-47e9ca75f25a", "Marilyn - Explainer"),
    "amelia":  ("043cfc81-d69f-4bee-ae1e-7862cb358650", "Amelia - Instructor"),
    "caroline":("f9836c6e-a0bd-460e-9d3c-f7299fa60f94", "Caroline - Southern Guide"),
}


def main():
    # CLI:  --voice bryce|sophie|clara|...     --speed 0.92     --no-play
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", default="bryce", choices=list(VOICES.keys()),
                    help="which Cartesia voice to use (default: bryce = Clear Explainer)")
    ap.add_argument("--speed", type=float, default=0.92,
                    help="speech rate; <1.0 is slower (default 0.92)")
    ap.add_argument("--no-play", action="store_true", help="skip afplay after synthesis")
    args = ap.parse_args()

    voice_id, voice_name = VOICES[args.voice]
    out = Path(f"/Users/mei/rl/explainer-{args.voice}.mp3")

    key = os.environ.get("CARTESIA_API_KEY")
    if key:
        try:
            print(f"voice: {voice_name}  (id={voice_id[:8]}…)  speed={args.speed}  model=sonic-2")
            synth_cartesia(SCRIPT, out, voice_id, key, speed=args.speed)
            print(f"wrote {out} ({out.stat().st_size // 1024} KB) via Cartesia sonic-2")
        except Exception as e:
            print(f"cartesia failed ({e}); falling back to macOS say")
            synth_macos_say(SCRIPT, out)
    else:
        print("CARTESIA_API_KEY not set; using macOS say")
        synth_macos_say(SCRIPT, out)

    # Audio safety: never play two streams at once. If afplay is already
    # running, kill it (the new audio is what the user wants now). If
    # --no-play was passed, just write the file and skip.
    if not args.no_play:
        running = subprocess.run(["pgrep", "-f", "afplay"],
                                 capture_output=True, text=True).stdout.strip()
        if running:
            print(f"afplay already running (pid {running.split()[0]}) — killing before playback")
            subprocess.run(["pkill", "-9", "afplay"], capture_output=True)
        print("playing...")
        subprocess.Popen(["afplay", str(out)])
        print(f"(playing in background — `pkill afplay` to stop)")


if __name__ == "__main__":
    main()
