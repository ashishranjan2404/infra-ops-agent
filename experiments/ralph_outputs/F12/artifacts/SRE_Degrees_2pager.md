# SRE-Degrees — The standardized test (and the practice problems) for incident-response AI

**One line:** We measure how good any AI model is at resolving real production outages, and we
generate the data that makes it dramatically better — without retraining the model.

---

## 1. The problem

When a large online service breaks, the clock is money. Big outages run into the millions per
hour, and the people who fix them — senior site-reliability engineers (SREs) — are scarce,
expensive, and burning out. Every company wants to put AI on the front line of these incidents.

The catch: real outages are traps. In a serious failure, one broken service quietly drags down
the services that depend on it. The alarm that screams loudest is usually firing on a **victim,
not the cause** — and the obvious fix (restart it, give it more capacity) often makes the
outage *worse*. Diagnosing this correctly is exactly the hard, judgment-heavy work that makes
senior SREs valuable, and exactly where today's AI quietly fails. The hard part was never
"restart the thing that's red." The hard part is figuring out *which* red thing is lying to you,
under time pressure, while the monitoring you'd use to investigate is itself degrading. That
skill takes years to build in a human and lives almost nowhere in training data.

## 2. Why now

Frontier AI models are finally good enough to read logs, reason about systems, and propose
fixes. But "good enough to look impressive in a demo" is not "good enough to trust during a 2am
outage." On realistic cascading failures, the best models off the shelf **get it right only
about a quarter of the time on the first try.** The capability is here; the reliability is not.
Whoever closes that gap owns the most expensive, highest-stakes corner of software operations.

## 3. The insight: graduate the system, not the model

Everyone else is trying to make outage-fixing AI better by *retraining the model* — slow,
expensive, and stale the moment systems change. We do the opposite. We keep the AI model
**frozen** and instead make the *code around it* smarter — a loop that watches the model
attempt a fix, checks it against reality, and feeds back what it got wrong so it can try again.
We call this **graduation**: the model stays the same, but the system it lives in keeps
leveling up. It works with any model, including next year's, on day one.

The second half of the insight is how we grade. We don't reward "did the service come back up" —
that's how you get an AI that restarts things until the dashboard turns green while the real
cause festers. We grade on the things a senior SRE actually cares about: **did it find the true
root cause, did it apply the correct fix, and did it avoid the trap.** That grader is the heart
of the system.

## 4. The evidence (real, measured)

We built a faithful simulator of cascading outages — failures that spread from a hidden root
cause to a loud victim, with a tempting wrong fix baked in — plus a copy running on a live cloud
cluster so the cascades are physically real, not scripted.

The headline result: our graduation loop lifts first-try success from **0.23 to 0.90** —
roughly a 4x improvement — on a full set of 42 incidents spanning simple, cascading, and
never-before-seen failure types. Crucially, **the same result reproduces on a second,
independent model** (0.24 → 0.89), and every fix is graded **by code, not by an AI judging its
own work.** The improvement and the baselines don't overlap — this is a real gap, not noise.[^1]

And the honest part: when we strip out the corrective feedback and keep only the retry
machinery, the improvement mostly vanishes — performance falls back near the baseline. We read
that as a feature, not a bug: **we know exactly where the lift comes from.** It's the quality of
the feedback content — and that feedback is precisely what we sell.

## 5. The product (and the wedge)

We are not pitching a robot that runs your outages unsupervised — that's the scary, far-off
version, and it's the expansion, not the ask. The wedge we ship first is concrete:

1. **The benchmark** — "the SAT for incident-response AI." A standardized, root-cause-aware way
   to score any model (or any vendor's agent) on realistic outages. Today there is no trusted
   yardstick; buyers are flying blind.
2. **The graded data feed** — "the practice problems." A stream of realistic, correctly-graded
   outage scenarios and solved trajectories — the raw material every team building outage AI
   needs and almost none can generate, because the hard part is grading the *reasoning*, not the
   outcome.

Land with measurement and data; expand into supervised, then increasingly autonomous, response
as trust is earned.

## 6. Market

The buyers are reliability and platform teams at any company where downtime is expensive: cloud
providers, fintech, e-commerce, SaaS, and the fast-growing set of companies building their own
operations AI. Observability and incident tooling is already a multi-billion-dollar category
(Datadog, PagerDuty, and peers); AI-for-operations ("AIOps") is one of its fastest-growing
slices *(directional estimate, not a measured figure)*. We sit one layer beneath all of them: the
evaluation and training data their AI features will be judged on and built from. Picks and
shovels, not a competing dashboard — we want every operations-AI team, including the incumbents'
own, to measure on our benchmark and train on our data.

## 7. Why it's defensible

Three compounding moats: (a) a proprietary catalog of **realistic cascade scenarios** drawn from
real post-mortems — the thing that's genuinely hard to build and easy to get subtly wrong; (b) a
**root-cause-aware grader** that resists the gaming every naive "did it recover" metric falls
for; and (c) the **graduation loop**, which gets better with every incident it sees while staying
model-agnostic. Competitors betting on a single fine-tuned model reset to zero every model
generation; we don't.

## 8. The ask

We're raising a **[seed round]** to turn a working research system into a product: harden the
benchmark into a hosted service, expand the cascade catalog, and sign the first design partners
among teams building operations AI. Concrete 12-month milestone: **the default third-party
yardstick that serious incident-response AI is measured against** — and the data feed those teams
train on.

The capability to automate the hardest part of running software is arriving. We make it
measurable, then make it reliable. That's the business.

[^1]: Rigor: full 42-incident set, 5 conditions, n=126 per condition (3 seeds), 630 episodes,
0 errors, deterministic (code-based) grader, non-overlapping 95% confidence intervals;
independently reproduced on a second model across 750 episodes with a paired significance test
(McNemar p<0.0001). Reward = 0.30·root-cause + 0.25·correct-fix + 0.45·resolved − 0.60·trap.
