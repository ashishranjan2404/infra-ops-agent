# H2 — 02 Grill (Ralph Loop, 5 personas x 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take

**SMR:** A pass@k gate on every PR is the right instinct — pass@k is the headline metric of
this repo and regressions in the eval substrate are silent killers. But running a *model*
sweep per PR is statistically meaningless: k small, seeds small, CIs huge. CI should guard
the *pipeline*, not benchmark a model.

**PSRE:** From an ops view the only acceptable CI is fast, hermetic, and non-flaky. Anything
that calls a gateway will flake on rate limits and 5xx and page nobody-but-annoy-everybody.
Hard requirement: zero network, zero secrets in the default PR job.

**REV:** As a reviewer I'd ask: what does this smoke actually *prove*? If it just asserts
"code runs", it's a tautology. It must assert a falsifiable invariant — e.g. the floor
property (cheapest path stays below threshold) and monotonic separation between a good and a
trivial policy. Otherwise it's green-theatre.

**RLE:** I want the smoke to reuse the *real* scoring path (`run_plan` -> `score_plan`,
deterministic judge), not a mock. If we mock the judge, the smoke can pass while the actual
reward wiring is broken. Use gold (canonical fix) and empty plans as the two fixed policies.

**DOL:** Workflow hygiene: pin action versions, set `timeout-minutes`, add `concurrency` to
cancel superseded runs, least-privilege `permissions: contents: read`, and `cache: pip`.
And critically — per the task — this file must NOT land in `.github/`; ship it as an
artifact a maintainer installs.

## Round 2 — react to another persona (genuine disagreement)

**RLE -> SMR:** I disagree that a model sweep is *useless* per PR. A nightly is fine, but I'd
want at least an *optional* gated job that runs a tiny real-model sweep on label, so a PR
that tanks pass@k on a real model can be caught before merge. SMR's "pipeline only" stance
risks shipping a regression that only shows up in the real metric.

**SMR -> RLE:** Counter: a tiny real-model sweep (k=2, 3 seeds) has a Wilson CI so wide it
can't *distinguish* a regression from noise. You'd either block good PRs on variance or pass
bad ones. A label-gated job is fine as future work, but it must never be a required check.
I hold my line: the *required* PR gate is deterministic.

**PSRE -> DOL:** I'll push back on DOL slightly — `cache: pip` can mask a broken
`requirements-rex.txt` (stale wheels). For a *deps* sanity gate I'd almost want cache off.
Compromise: keep cache for speed but ensure the install step would fail loudly on a bad pin.

**REV -> RLE:** RLE's gold-vs-empty is good but I found a hole: if a *single* scenario's
canonical fix is mis-specified (data bug), a strict `gold pass@1 == 1.0` assertion turns a
data issue into a red CI on unrelated PRs. That's a false-positive failure mode. The
invariant must tolerate one bad scenario while still catching a substrate regression.

**DOL -> PSRE:** Agree on cache nuance, but disagree it's worth turning off — a deps gate
isn't this job's purpose; the test+smoke is. If we want a deps-freshness gate that's a
separate scheduled job. Keep cache on; keep this job fast.

## Round 3 — synthesis

Consensus:
- **Required PR gate = deterministic only** (SMR/PSRE win): pytest subset + LLM-free pass@k
  smoke. No secrets, no network, `timeout-minutes`, pinned actions, concurrency, least-priv.
- **Smoke must assert falsifiable invariants** (REV/RLE): reuse the *real* scoring path;
  enforce SEPARATION (gold > empty), FLOOR (empty pass@1 == 0), and a tolerant GOLD-FLOOR
  (gold pass@1 >= 0.8) so one mis-specified scenario can't redden unrelated PRs (REV's hole).
- **Real-model sweep = future, label-gated, non-required** (RLE's want, SMR's guardrail).
- **Ship as artifact, not in `.github/`** (DOL + task rule).
