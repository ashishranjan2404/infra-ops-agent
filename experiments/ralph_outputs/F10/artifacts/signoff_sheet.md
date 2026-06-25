# SRE-Degrees — Co-Author Claim Sign-Off Sheet

**Purpose:** Before submission, every major paper claim must be confirmed by all
three co-authors. This sheet pairs each claim with its concrete evidence pointer
and a sign-off column per author. A claim is *cleared* only when all three columns
read `APPROVED`.

**Grounding:** All claims, evidence pointers, and caveats are taken verbatim from
`experiments/CLAIMS_EVIDENCE.md` (the single source of truth from the meeting,
Ashish's framing). Do not re-state numbers here that are not in that file.

**Authors:** Ashish (lead / framing), Wenji (training / GRPO + Fireball), Sylvie (SRE / incident realism).

**Sign-off legend:** `PENDING` (not yet reviewed) · `APPROVED` · `APPROVED w/ comment` · `REJECTED` (see comment).
This is a *coordination* artifact: the Ralph worker cannot set any cell to APPROVED.
Every cell ships as `PENDING` until a human author edits it. See `BLOCKER.md`.

---

## A. Primary scientific claims

| # | Claim (paraphrased — full text below) | Evidence pointer | Key number | Known caveat (from CLAIMS_EVIDENCE.md) | Ashish | Wenji | Sylvie |
|---|---|---|---|---|---|---|---|
| C1 | Synthesized 3-rule safety harness blocks trap actions, approaches hand-written perf on simple incidents | `rex/runs/harness_synth_v2.json`; Diagram 5 | Synth v2 89.7% acc vs hand-written 94.9%; 10→3 rules | Missing pass@1 on simple-only split; no no-harness baseline on same incidents; Haiku only | PENDING | PENDING | PENDING |
| C2 | FIREBALL (D&D) transfer-learning fine-tune improves pass@1 on cascade/multi-hop incidents, beats OpenSRE | Wenji's GRPO run (**NOT YET PUSHED** to repo) | Fireball > OpenSRE on cascade; slightly worse on simple | Single run, not replicated by Ashish; no pass@k; branch unpushed; untested on 19 real incidents | PENDING | PENDING | PENDING |
| C3 | REx + SME feedback (code-as-policy) beats zero-shot / best-of-n / retry by ≥2x pass@1 on complex incidents; gain vanishes without oracle | `rex/runs/ablation.json`; Diagram 4 | REx-SME 0.687 vs zero-shot 0.242 (2.8x); REx-no-oracle 0.250 (no lift) | 4 non-REx baselines indistinguishable (0.23–0.25), Wenji flagged "too close"; mean reward not pass@k; Haiku only; SME semi-synthetic | PENDING | PENDING | PENDING |

## B. Supporting / figure-level claims

| # | Claim | Evidence pointer | Status (from mapping table) | Ashish | Wenji | Sylvie |
|---|---|---|---|---|---|---|
| S1 | Diagram 1: zero-shot diagnosis baseline | `rex/runs/frontier.json` | Have data, needs pass@k | PENDING | PENDING | PENDING |
| S2 | Diagram 2: REx vs baseline across 5 models | `rex/runs/frontier.json` | Have data, needs pass@k | PENDING | PENDING | PENDING |
| S3 | Diagram 3: REx with/without oracle | `rex/runs/ablation.json` | Have data, needs pass@k | PENDING | PENDING | PENDING |
| S4 | Diagram 5 false-allows are genuinely unlearnable (2 unseen, 2 even hand-written misses) | `experiments/CLAIMS_EVIDENCE.md` L106-109 | Strongest result, solid | PENDING | PENDING | PENDING |

## C. Negative / blocked results (must be disclosed, also need sign-off)

| # | Claim / disclosure | Evidence pointer | Status | Ashish | Wenji | Sylvie |
|---|---|---|---|---|---|---|
| N1 | Diagram 6 fine-tuning is INCOMPLETE: 8B reward FLAT (0.522→0.491) over 25 steps; 8B/30B crashed | `experiments/CLAIMS_EVIDENCE.md` L94, L127-131 | Incomplete — do NOT claim as positive | PENDING | PENDING | PENDING |
| N2 | RLVR harness-in-loop ambiguity: unclear if RLVR ran with or without harness; must clarify before any fine-tuning claim | `experiments/CLAIMS_EVIDENCE.md` L131 | Open question | PENDING | PENDING | PENDING |

---

## Full claim text (verbatim from CLAIMS_EVIDENCE.md)

**C1 (Claim 1):** "A Thompson-sampling-synthesized safety harness (3 auto-generated
rules) blocks trap actions and improves pass@1 on simple incidents, approaching
hand-written rule performance."

**C2 (Claim 2):** "Fine-tuning on FIREBALL D&D trajectory data (structured
state-transition data from a non-SRE domain) improves pass@1 on cascade/multi-hop
incidents, outperforming OpenSRE-trained agents."

**C3 (Claim 3):** "REx with SME feedback (code-as-policy from expert corrections)
outperforms zero-shot, best-of-n, and retry-realistic by ≥2x on pass@1 for complex
incidents. Without SME feedback (REx-no-oracle), the gain disappears."

---

## Per-author responsibility map (suggested reviewer of record)

Each claim should have a *primary reviewer* — the author whose domain owns the
evidence — in addition to the two confirmatory sign-offs.

| Claim | Primary reviewer (owns evidence) | Why |
|---|---|---|
| C1 harness | Ashish | Owns REx harness synthesis / framing |
| C2 Fireball | Wenji | Ran the GRPO/Fireball training; must push branch |
| C3 REx+SME | Ashish | Owns code-as-policy ablation |
| S4 false-allows | Sylvie | SRE realism — is_safe miss is an incident-semantics call |
| N1/N2 fine-tuning | Wenji | Owns training runs / RLVR config |

## Blocking conditions before any cell can be APPROVED

1. **C2 cannot be reviewed until Wenji pushes the GRPO branch** — the evidence is
   not in the repo (`CLAIMS_EVIDENCE.md` L38). C2 is therefore *unreviewable* today.
2. **N2 must be resolved** (RLVR with/without harness) before C2 or N1 sign-off,
   because it changes the interpretation of the fine-tuning results.
3. Sign-off requires the author to have actually opened the cited evidence file.

## How to use this sheet

1. Each author edits ONLY their own column.
2. Replace `PENDING` with `APPROVED`, `APPROVED w/ comment: <text>`, or `REJECTED: <text>`.
3. Run `python3 check_signoff.py signoff_sheet.md` to see the cleared/blocked tally.
4. A claim ships only when its row is all-`APPROVED`. Track residual blockers in `BLOCKER.md`.
