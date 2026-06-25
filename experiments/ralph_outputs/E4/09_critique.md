# E4 — 09 Critique (honest)

## The headline weakness: the actual result is BLOCKED
This task asks "does Fireball-trained hurt vs OpenSRE-trained on simple incidents?"
and the honest answer tonight is **we cannot say** — neither trained checkpoint
exists in the repo. I delivered the *measurement instrument* + a stand-in run, not
the finding. A reviewer is entitled to say "you answered a different question."
Mitigation: the deliverable scope (harness + honest blocker) is exactly what the
brief authorises when the model is blocked, and the blocker is independently
corroborated (`P7_fireball_status.md`).

## Where a reviewer attacks
1. **Stand-in verdict optics.** `verdict: B_HURTS` over glm-5p2 vs minimax-m3 says
   nothing about Fireball or OpenSRE — it's two unrelated generalists differing on 8
   tasks. If quoted out of context it's actively misleading. I carry an in-band
   `note` and label policies `*_standin`, but the risk is real.
2. **Statistical power.** 3 seeds → per-incident pass@1 ∈ {0, .33, .67, 1.0}; the
   Wilson CIs are huge. No delta here is significant. Fine for an instrument demo,
   useless as evidence. The real run needs ≥8 seeds (I expose `--seeds`).
3. **"Simple" is by label, not proven-easy.** I validate family membership, not that
   a strong generalist scores ~1.0 on all 8. In the stand-in, glm-5p2 itself scored
   0/3 on `oom_kill` and `singleton_node_notready` — so either those aren't truly
   "simple" for this judge, or the deterministic judge is strict there. Worth a
   follow-up calibration before drawing transfer conclusions.
4. **Cross-provider apples-to-oranges (future).** The real run will likely pit a
   forked Qwen (Tinker) against another provider; Fireworks prepends system into the
   prompt (`agent/llm.py`), so trained-vs-trained scores won't be strictly
   comparable. The artifact records provider so the caveat travels, but it's a
   genuine confound for the eventual finding.
5. **Zero-shot only.** I compare single-shot policies. If the thesis is about
   *deployed* behaviour, multi-turn / REx-wrapped comparison might tell a different
   story. Out of scope here but a legitimate gap.

## What's missing
- A calibration pass showing a strong generalist (Claude/GPT) near-ceilings the 8 —
  blocked tonight by the Anthropic 400 and empty gateway responses.
- The two trained slugs (the whole point).

## Honest bottom line
Solid, reproducible, scope-clean instrument; real stand-in numbers; **blocked** on
the science. I did not fabricate a Fireball result, and I did not let the stand-in
verdict pose as one.
