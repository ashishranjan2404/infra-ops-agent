# F11 — 02 Grill: 5 personas × 3 rounds

Personas: **SR** Senior ML Researcher · **PSRE** Principal SRE · **REV** AAAI Reviewer ·
**RLE** RL Engineer · **DEV** DevOps Lead.

## Round 1 — initial take

**SR:** An artifact appendix is only useful if the headline claim has a one-command repro.
The headline here is "REx > best-of-N on novel incidents." I want the appendix to name the
exact `--conditions rex,best_of_n --per-family ... --seeds ...` invocation and the JSON key
to read (`by_condition.rex.by_family.novel["pass@1"]`).

**PSRE:** As the SRE on the committee I care that the *substrate is real*. These scenarios are
modeled on actual postmortems (Cloudflare, Slack, GitHub, Knight Capital). The appendix must
disclose that the world is a simulator (`sim/engine.py`), not a live cluster — otherwise an
evaluator thinks they need a Kubernetes bill to reproduce.

**REV:** For the *Available* badge I need a DOI-able, frozen artifact (Zenodo/figshare), not
just "git clone main." Main moves. The appendix must pin a commit/tag. For *Reproduced* I need
the tolerance: how close must my pass@1 be to the paper's to count as reproduced?

**RLE:** The grading is deterministic (`REX_JUDGE_MODE=deterministic`), which is great — it
means re-running grading on cached plans is bit-reproducible. But the *proposer* is a sampled
LLM at temperature 0.7. So the metric has Monte-Carlo noise. The appendix MUST report the
Wilson CI and say "reproduced = within overlapping 95% CI," not exact equality.

**DEV:** I'll be the one running it in a clean container. Give me a Dockerfile or at minimum a
pinned `requirements-rex.txt` + exact Python version + the env vars needed and which are
optional. And give me an *offline* path so I can earn Functional without a paid API key.

## Round 2 — react to another persona by name (genuine disagreement)

**RLE → SR:** I disagree with SR's "one-command repro = the headline." The full sweep across
5 conditions × 3 families × N seeds × an LLM call per episode is *expensive and stochastic*.
Selling it as a single cheap command is misleading. The appendix should tier it: a cheap
offline *Functional* tier and an expensive online *Reproduced* tier with an estimated cost and
wall-clock. One command, yes — but be honest that the headline tier costs money.

**REV → PSRE:** I push back on PSRE treating "it's a simulator" as a mere disclosure. For an
AAAI artifact, a *simulator* is actually a strength for reproducibility — but only if it's
**deterministic given a seed**. PSRE frames it defensively; I want it framed as a feature, AND
I want proof the sim is seed-deterministic. If `run_plan` has hidden nondeterminism the whole
"deterministic grading" claim is hollow.

**PSRE → DEV:** Disagree with DEV's "give me a Dockerfile." We do NOT control the LLM gateway;
a Dockerfile pins Python deps but not the model behind `agent/llm.call`. A frozen container
gives a false sense of hermeticity. Better: pin deps via requirements-rex.txt, and for the
*online* tier explicitly version the model slug (e.g. `glm-5p2`) and warn that gateway model
updates can shift numbers — that's a known, declared threat to reproduction, not a bug.

**SR → REV:** I partly reject REV's "must be on Zenodo or no Available badge." Available only
requires a *persistent public* archive; a tagged GitHub release with an archival snapshot is
commonly accepted, and Zenodo can mint a DOI *from* a GitHub release. So the appendix should
recommend the GitHub-release→Zenodo path, not demand a hand-uploaded tarball. But I concede
REV's tolerance point entirely: we must state the reproduction tolerance numerically.

**DEV → RLE:** Agree the online tier is stochastic, but I disagree that means "no determinism
claim." The *offline Functional* tier (registry load + floor check + deterministic-judge unit
tests) IS bit-deterministic and credential-free. That's the tier I'll actually use to grade
Functional. Don't bury it under the expensive tier.

## Round 3 — synthesis

Consensus the appendix must encode:
1. **Two-tier evaluation.** Tier A (offline, free, deterministic): registry load + floor check
   + `tests/test_rex_deterministic_judge.py`. Earns **Functional**. Tier B (online, costs API
   $, stochastic): the full `rex.eval_pass_at_k` sweep. Earns **Reproduced**.
2. **Honest substrate disclosure**: world is `sim/engine.py` (deterministic given seed),
   scenarios modeled on real postmortems; grading deterministic; *proposer* stochastic.
3. **Numeric reproduction tolerance**: a run reproduces if its per-condition pass@1 falls in
   the paper's reported Wilson 95% CI (or CIs overlap). State seeds & per-family used.
4. **Availability path**: pin a git tag/commit; recommend GitHub release → Zenodo DOI.
5. **Declared threats to repro**: gateway model drift (slug versioning), API cost/time, sample
   noise — all disclosed, not hidden.
6. **Self-checking**: ship a badge_claim_map.json + a pytest that asserts the named files/flags
   exist so the appendix can't silently rot.
