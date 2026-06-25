# SRE-Degrees — 15-Minute Talk Outline
### "You can improve a model at anything you can verify — so we learned the verifier."
*A verifiable RL environment for safe autonomous incident response.*

Format: 17 content slides, ~15:00 total. Each slide: **key point** + **timing** + speaker note.
Every number traces to `ARCHITECTURE.md` or `docs/headline_insights.md` in the repo.
Timing budget validated by `timing_check.py` (sums to 15:00, no slide > 75s).

Legend for source tags: `[ARCH]` = ARCHITECTURE.md, `[HEAD]` = docs/headline_insights.md.

---

### Slide 1 — Title (0:30)
**SRE-Degrees: a verifiable RL environment for safe incident response.**
Subtitle: *frozen LLM as policy, root-cause-aware reward, a safety verifier we searched for
instead of writing.* Authors / affiliation / repo link.
> Note: One sentence — "This is a talk about making an LLM reliable at on-call without touching
> its weights, by building the environment and reward instead." Set expectation: an ML talk
> grounded in real outages.

### Slide 2 — Hook: the alert is lying to you (1:15)
**Key point:** A real production cascade fires its loudest alert on the *victim*, not the
cause — and the naive fix makes it worse. Walk one reconstructed real outage (e.g. AWS
DynamoDB DNS, or Cloudflare WAF). `[ARCH]`
> Note: Tell it as a story. Service B is paging. You scale B. B keeps dying because A (upstream,
> silent) is the real cause; scaling B herds load and *worsens* it. Frontier models fall for
> this on the first try. ~60s, no equations.

### Slide 3 — The ML problem (0:45)
**Key point:** Two questions: (1) can a *frozen* frontier model handle this cascade, and
(2) can we *verify* when it's actually right — not just "did the metric come back up"? `[ARCH]`
> Note: This is the pivot from war-story to ML. "Did it come back up" is reward-hackable: restart
> until green. The hard part is verifying *root cause + correct fix + no trap*.

### Slide 4 — Why existing benchmarks don't cut it (0:45)
**Key point:** Public SRE/agent benchmarks are memorizable, score on outcome only, and rarely
encode the trap. We build from public post-mortems into graded root-cause + fix + safety
tasks where cascades are *derived*, never scripted. `[HEAD]` `[ARCH]`
> Note: Emphasize "not a toy, not a memorized leaderboard." The cascade is emergent from a typed
> dependency graph, so you can't pattern-match the answer.

### Slide 5 — Environment vs policy (the framing that matters) (0:45)
**Key point:** The LLM is a **frozen, swappable policy** — no fine-tuning. Reliability comes
from the **environment + a root-cause-aware reward**, code-as-policy / auto-harness style. `[ARCH]`
> Note: Say it plainly so nobody mis-files this: "We did not make the model smarter. We built an
> environment that exposes when it's right and penalizes when it's confidently wrong."

### Slide 6 — The environment (system diagram) (1:15)
**Key point:** One scenario DSL → emergent cascade engine. Declarative topology + hidden root
cause + trap + correct fix; `propagate()` makes cascades emergent and deterministic.
~9 CIDG + a larger real-outage catalog. `[ARCH]`
> Note: Use the system diagram. Stress single-source-of-truth specs and that the cascade is
> *derived* by one kernel — cheap, seedable, reproducible.

### Slide 7 — The reward: anti-gaming is the crux (1:15)
**Key point:** `score = 0.30·diagnosis + 0.25·correct_fix + 0.45·resolved − 0.60·trap`.
"Resolved" alone is only 45% — misdiagnose or trip the trap → **0.0**. Diagnosis is an
LLM-judge on the *mechanism*; the trap (scale a crash-looping control plane → herd its
datastore) costs −0.60. `[ARCH]`
> Note: This is the technical heart. Walk each term. The point: this is what gives the data real
> within-group signal instead of reward-hackable noise. ~75s, the longest setup slide.

### Slide 8 — Within-group signal (env quality) (1:00)
**Key point:** On one-shot diagnosis the env lands in a **20–50% reward band with real
variance** and cleanly separates weak from strong: haiku **0.27** vs opus **0.50** mean. `[HEAD]`
> Note: This proves the env is discriminative — it's not saturated and not floored. The spread
> is the asset for any downstream RL.

### Slide 9 — REx: refine a frozen model in the loop (0:45)
**Key point:** REx = a Thompson-sampling tree over candidate refinements: propose → harness
feedback → refine, behind a safety gate. Wraps a frozen model, same reward. `[ARCH]`
> Note: Keep brief — it's the loop that *uses* the env. The honest verdict on its lift comes in
> two slides; don't oversell here.

### Slide 10 — Headline result: the searched safety verifier (1:15)
**Key point:** We don't hand-write the safety harness — we **search** it. A Thompson-tree over
rules-as-data (no LLM code execution) discovers the verifier: trained on 7 incidents, it gates
unsafe actions on **3 held-out incidents at 0.90 accuracy vs 0.95 hand-written**, compressing
**14 → 3 general rules** with zero synthesis-quality misses. `[HEAD]`
> Note: This is the strongest *novel* result. Scope it honestly out loud: "generalizes to
> hazards present in training; the one held-out miss is a hazard absent from training — you
> can't invent the unseen." Small n (3 held-out) — say so before a reviewer does.

### Slide 11 — Two-tier reality contract (proof it isn't a toy) (0:45)
**Key point:** Tier-A = fast in-process sim (the data engine). Tier-B = a live GKE call-mesh
where services call each other over real HTTP, Prometheus/Alertmanager fire on the *victim*.
We only claim sim≈cluster for mechanisms pinned on the real mesh. `[ARCH]`
> Note: One Grafana screenshot of the alert on the victim. State the honest contract: everything
> else is "structurally faithful, numerically unvalidated." Credibility through restraint.

### Slide 12 — Self-audit: we stress-tested our own headline (1:15)
**Key point:** A fair-control ablation shows REx's *refinement* lift was largely
**oracle-feedback leakage**: strip the root-cause hint and REx **0.25 ≈ zero-shot 0.24**;
best-of-N (0.24) and outcome-only retry (0.23) add ~0. **The defensible contributions are the
verifiable environment and the searched verifier — not the refinement loop.** `[HEAD]`
> Note: The most important slide for credibility. Deliver it confidently: "We audited our own
> best number and report where it didn't hold." This *earns* trust for slides 8 and 10.

### Slide 13 — Curriculum: simple → hard makes it legible (1:00)
**Key point:** 15 single-leaf incidents (alert = cause) vs 5 reconstructed real cascades (alert
= victim, naive fix worsens). On the hard tier models floor at ~0.19–0.42 zero-shot; the
hardest three are *escalated*, not faked. `[ARCH]`
> Note: Show the difficulty gradient chart (`docs/curriculum_rewards.png`). Point: the env has
> headroom for training and the safety gate holds — models escalate the unsolvable instead of
> flailing.

### Slide 14 — Limitations (honest) (0:45)
**Key point:** Small held-out set for the verifier (n=3); sim numbers ≠ cluster numbers beyond
pinned mechanisms; refinement-loop lift not defensible under fair control; LLM-judge on
mechanism is itself a model. `[HEAD]` `[ARCH]`
> Note: Don't rush — a clean limitations slide is a strength signal at AAAI. Each item maps to a
> claim we *did not* make.

### Slide 15 — Related work / positioning (0:30)
**Key point:** Versus outcome-only agent benchmarks and reward-modeling work: our novelty is a
*verifiable* incident env with a trap-aware reward and a *learned* verifier (rules-as-data
search), not a fixed leaderboard.
> Note: Fast. One sentence each on benchmark-style work, reward modeling, and verifier search.

### Slide 16 — Contributions (0:45)
**Key point:** (1) A verifiable, reproducible incident-response RL environment with a
trap-aware, anti-gaming reward and real within-group signal; (2) a *searched* safety verifier
that generalizes to held-out hazards (14→3 rules, 0.90 vs 0.95); (3) an honest ablation
relocating the rigor to env + verifier. `[HEAD]`
> Note: Three crisp bullets. These are exactly the claims that survived the self-audit.

### Slide 17 — Close + reproduce it yourself (0:30)
**Key point:** "You can improve a model at anything you can verify — so we learned the
verifier." Repo + one-command reproduce (`HUD_API_KEY=… python3 -m rex.frontier`). Q&A. `[ARCH]`
> Note: End on the thesis sentence. Invite the room to run it. Hand to Q&A with backup slides ready.

---

## Timing summary
0:30 + 1:15 + 0:45 + 0:45 + 0:45 + 1:15 + 1:15 + 1:00 + 0:45 + 1:15 + 0:45 + 1:15 + 1:00 +
0:45 + 0:30 + 0:45 + 0:30 = **15:00** across 17 slides.

## Backup slides (Q&A only, not in the 15 min)
- **B1 — Reward term sensitivity:** what happens if you drop the −0.60 trap penalty (data
  becomes reward-hackable).
- **B2 — Full REx-lift table** (0.63–0.81 → 0.86) *with* the ablation caveat, for the inevitable
  "but your slide said REx helps" question. `[ARCH]`
- **B3 — Verifier search internals:** Thompson-tree over rules-as-data, 14→3 rule compression,
  the single held-out miss explained. `[HEAD]`
- **B4 — Tier-B infra:** GKE call-mesh topology, kube-prometheus-stack, alert-on-victim wiring.
- **B5 — Open-model training status:** GRPO/RFT on Qwen3-8B/30B via HUD Tinker; easy tier flat
  near ceiling (~0.5), harder cascades (headroom ~0.35) underway. `[HEAD]`
