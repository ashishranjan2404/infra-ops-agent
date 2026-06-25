# Snorkel AI — Contact & Positioning Brief (for SRE-Degrees outreach)

> Status: research package for a human to act on. **Sending the email is out of
> scope for the automated worker** — no mailbox, no authority to commit a
> partnership. Verify the flagged items before sending.

## 1. Who Snorkel is (and why they fit)
Snorkel AI is an "expert data for frontier AI" company (Series D, ~$100M raised,
May 2025). Beyond data labeling they now **build runnable RL environments and
agentic benchmarks** with deterministic / verifiable rewards — directly adjacent
to what SRE-Degrees does. Their published RL-environment domains include:

- **Terminal / OS** (real shells, package managers, filesystems — Terminal-Bench 2.0 contributions)
- **Browser / Web**, **General Assistant** (multi-tool orchestration)
- **Tool Mastery & Safety** (API/tool use, red-teaming)
- **Finance & Insurance** (SnorkelUnderwrite, Finance Reasoning benchmarks)

Their methodology = a domain expert writes a PRD of the real workflow, tools, and
success criteria; the env runs as either "Simulated Agentic Evaluation" or an
"RL Gym," graded by **verifiable endpoints (unit tests, state asserts, DB diffs)**
rather than subjective rubrics. This is *exactly* our model (sim cluster + trap
actions + canonical-fix verifier). An SRE/incident-response RL environment is a
natural, currently-unfilled slot in their domain lineup.

## 2. Why them specifically (leverage)
- They publicly fund **open benchmarks**: a stated **$3M Open Benchmarks Grants**
  program for "open-source datasets, benchmarks, and evaluation artifacts."
- They run a **Research Collaboration** track (co-developing benchmarks/eval
  frameworks) and **Expert Data-as-a-Service**.
- We arrive with a *built, verifier-shaped* incident dataset (19 cascade
  incidents reconstructed from first-party postmortems, a sim engine, a
  deterministic judge, and an ingest schema). We're a credible co-author, not a
  data supplicant.

## 3. Researched contact paths (only real channels)
| Channel | URL | Use | Confidence |
|---|---|---|---|
| Partner / collaboration form | `https://snorkel.ai/partners/` ("Become a partner" → `/talk-to-an-expert-ai-solutions/`) | Primary: research collaboration / open benchmark | Confirmed (page) |
| "Talk to a data researcher" | on `snorkel.ai/partners/` | If framed as data-dev engagement | Confirmed (page) |
| General contact | `https://snorkel.ai/contact/` | Fallback routing | Confirmed (page) |
| Expert Contributor portal | `https://experts.snorkel-ai.com/home/` | NOT for us (SME signup) — ignore | Confirmed (page) |
| LinkedIn company | `https://www.linkedin.com/company/snorkel-ai` | Warm-intro / DM route to named staff | Confirmed |

**Target persona / ideal recipient:** **Armin Parchami, Sr. Director, R&D**
(public author of Snorkel's RL-environments work). Route via the partner form or a
warm LinkedIn intro. **Do NOT fabricate or guess his email address** — none was
found in research; an invented address will bounce or annoy. If a warm intro
exists through the team's network, that beats the cold form.

> Verify-before-send: confirm the partner-form URL still resolves and that
> Parchami is still the right R&D lead at send time (titles change).

## 4. The ask (tiered)
**Primary (moonshot):** co-develop an **open SRE / incident-response RL
benchmark** — a runnable incident environment with verifiable rewards — fundable
under their Open Benchmarks Grants. We bring the sim + 19 reconstructed cascade
incidents + schema; they bring expert-data scale and (ideally) anonymized
real-incident structure.

**Fallback (low-friction):** even a handful of **anonymized, structured incident
records** (symptom → trap action → root cause → fix, *not* raw logs) under NDA,
enough to validate our ingest schema and de-risk a larger collaboration.

CTA: a 30-minute exploratory call.

## 5. What this buys us — and what it does NOT (honesty)
- **Buys:** third-party-authored, verifier-ready incidents → breaks our
  *self-authoring / contamination* problem (today every scenario is authored by
  us, which a reviewer attacks). A credible partner also strengthens the paper's
  external-validity story.
- **Does NOT buy:** this does **not** close the "0 fully real raw incidents" gap
  flagged in `experiments/INCIDENT_DATASET.md`. Snorkel's model is *expert-
  constructed* data; their records would be reconstructed/curated, not raw prod
  logs. Do not represent partner data as "fully real raw incidents" in the paper.
  It changes *who held the pen*, not the synthetic-vs-raw axis.

## 6. Out of scope for this artifact
No email was sent. No partnership was initiated or committed. Legal/data-sharing
terms are gated by `data_sharing_checklist.md` and must be settled by a human
before any data changes hands.
