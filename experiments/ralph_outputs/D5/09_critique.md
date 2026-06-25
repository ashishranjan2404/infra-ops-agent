# D5 — 09_critique (honest)

## What a reviewer will attack
1. **The headline number is missing.** The deliverable answers "which gives the bigger gain?" with a
   *protocol and a proxy ceiling*, not a trained delta. The actual RFT-vs-SFT comparison is blocked
   on compute + the SFT SDK surface. This is the central weakness: it's a well-instrumented promise,
   not a verdict. Mitigation is honesty (no faked numbers), but a reviewer wanting the answer leaves
   unsatisfied.
2. **Circular-ish proxy.** The proxy ceiling grades the SAME demos selected as "best." It's held out
   from SFT-target *selection* (eval split), so it's not fully circular, but it is still an upper
   bound on cloning, not evidence either regime reaches it. The 1.000 mechanism_match is a giveaway
   that the mechanism term saturates on strong demos — informative for headroom analysis, but it
   inflates the proxy and could mislead a skim reader despite the caption.
3. **Multi-teacher SFT target.** "Best per scenario" mixes Opus/Haiku/Kimi. That's defensible (RAFT)
   but means the SFT teacher is incoherent; a purist would demand a single-teacher ablation.
4. **Grader-version mismatch.** Pooled `reward` was computed by an earlier grader; the harness
   recombines stored subscores with v2 weights and recomputes mechanism with `red_herrings=[]`
   offline (we don't have the herring list without importing SCENARIOS). So the offline mechanism
   term is optimistic. A full run should grade through the real `hud_env_v2._grade_v2`.
5. **Small data.** 34 scenarios, 10 eval. Any trained delta will have wide error bars; single-seed
   results would be uninterpretable. The protocol needs multiple seeds — noted but not run.
6. **SFT can't touch the tail.** 3 scenarios have no qualifying demo, so SFT structurally cannot
   learn them while RFT can attempt them. That biases the comparison in RFT's favor on the tail and
   should be reported per-split, which the harness supports but the trained run hasn't exercised.

## What's genuinely solid
- "Same data" is auditable (frozen seeded split, shared by both configs, asserted by tests).
- The SFT-SDK blocker is *verified by introspection*, not assumed — a sharper finding than "no GPU."
- The proxy ceiling yields a real, useful insight: remediation_tool ≈ 0 and ruled_out ≈ 0.27 in the
  best demos, so SFT's ceiling is ~0.68 and those two terms are exactly where RFT has room to win
  (motivates H2 quantitatively).

## Honest status
Deliverable (plan+spec+runnable harness+configs+tests+report scaffold) is COMPLETE and real; the
downstream trained comparison is BLOCKED (compute + SFT SDK). Per the brief, status = completed with
the blocker noted.
