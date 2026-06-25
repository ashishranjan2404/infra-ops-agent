# D5 — 02_grill (Ralph Loop, 5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (AR)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR.** The cleanest framing is RFT-as-RAFT vs vanilla SFT, both on the same scenario split. But
be precise about "same data." SFT on the *best existing trajectory per scenario* is rejection
sampling = exactly the demonstrations RFT would converge toward. So a fair contrast is: SFT clones
the argmax-reward demo; RFT optimizes against the grader directly. Expectation from the literature
(STaR, RAFT, RLHF ablations): SFT on good demos gives a fast, large first-step gain; RFT adds a
smaller but *further* gain on top, especially on within-distribution mechanism discrimination.

**PSRE.** From an on-call view, what matters is the *category* term and not over-claiming. The demos
in the pool come from Opus/Haiku/Kimi — strong models. SFT will clone their style including their
hedging. If the base trainee is Qwran-8B, cloning Opus answers may actually be the dominant gain and
RFT barely moves it. The honest question is "is there headroom left after SFT for RFT to capture?"

**AR.** This will get desk-rejected if "same data" is hand-waved. You must show the train/eval split
is identical and frozen, that the eval grader is identical, and that the base model is identical.
Also: a single seed proves nothing. And reporting reward on *training answers* as if it were a
post-training result is a fatal flaw — label proxies as proxies.

**RLE.** GRPO needs within-group reward spread or the advantage is zero. train_rft_v2's whole point
was fixing the flat baseline by adding the graded mechanism term and 10 tasks. If the SFT leg
collapses output diversity, a *subsequent* RFT leg would have low spread and learn nothing — order
matters. Decide: are we comparing SFT-vs-RFT (parallel, both from base) or SFT-then-RFT (sequential)?

**DOL.** Both legs need the `.venv-hud` 3.12 env, a forked Qwen slug, and HUD Tinker credits. The
RFT loop already hits transient 502s. SFT needs a token-level supervised endpoint — does the Tinker
provider even expose forward/backward on supervised targets, or only on rollout batches? If not, the
SFT leg is blocked at the SDK level, not just on compute. Verify the API surface before promising.

## Round 2 — react to another persona by name (forced disagreement)

**RLE → SMR.** I disagree with SMR's "RFT adds a smaller further gain" as the default expectation.
On THIS env the reward is a *deterministic keyword grader*. RFT can reward-hack it — stuff required
keywords without real reasoning — and score higher than the cloned Opus demo while being worse SRE.
So RFT may show a *bigger* number that's partly hacking. The comparison must include a hack check
(keyword-stuffing detector), or RFT "winning" is an artifact.

**AR → DOL.** DOL is right that the SDK surface is the real blocker, and that *kills* the headline
claim if unaddressed. But I disagree it should stop the deliverable. A pre-registered protocol +
runnable offline harness + honest blocker is a legitimate contribution; a fabricated win is not. The
paper here is the *methodology and the proxy result*, not a trained number we don't have.

**PSRE → SMR.** I push back on SMR treating the Opus/Haiku/Kimi demos as gold. Several pooled
trajectories have reward ~0.22 (I saw one in the data). "Best per scenario" can still be a mediocre
demo if no model solved that scenario. SFT will then clone garbage for the hard scenarios. We need a
*reward threshold* on the SFT targets and to report how many scenarios have no qualifying demo.

**DOL → RLE.** RLE's sequential-vs-parallel question is the one that decides the whole compute plan.
I disagree with leaving it open: pick **parallel, both from the same base**. Sequential SFT→RFT is a
third condition that doubles cost and confounds "which gives the bigger gain" with ordering. Ship the
parallel comparison; note SFT→RFT as future work.

**SMR → RLE.** Conceding the hack point but disagreeing on severity: the v2 grader already credits
mechanism via `mechanism_score`, which divides gold hits by (gold+herring) hits — pure keyword
stuffing of red-herring terms *lowers* the score. So the grader is partly hack-resistant. Still,
RLE's keyword-stuffing check is cheap insurance; add it as a diagnostic column, not a gate.

## Round 3 — synthesis

Consensus deliverable:
1. **Parallel comparison**, both legs from the *same base model* on the *same frozen split*
   (`split.json`), evaluated by the *same v2 grader*. (DOL+RLE resolved ordering.)
2. **SFT targets = best trajectory per train scenario with reward ≥ threshold**; report coverage
   (how many train scenarios have a qualifying demo). (PSRE.)
3. **Pre-registered metric**: mean held-out v2 reward, delta vs base, with a hack-diagnostic
   (required-keyword density + red-herring density) reported alongside. (RLE+SMR.)
4. **Honest about the blocker**: verify the Tinker SDK supports supervised forward/backward; if not,
   the SFT leg is SDK-blocked and we ship the scaffold + offline proxy only. (DOL+AR.)
5. **No proxy presented as a trained result.** The offline harness computes a *proxy ceiling*
   (grader on existing best demos) clearly labeled as such. (AR.)
