# RFT vs SFT on Identical Incident-Diagnosis Data — Comparison Report (scaffold)

## 1. Question
On the SAME opensre incident-diagnosis data, which post-training regime gives the bigger gain
over the base trainee: RFT (GRPO/RLVR) against the deterministic grader, or SFT on the best
existing demonstrations?

## 2. Setup (held fixed across both legs)
| Knob | Value |
|---|---|
| Base model | opensre-qwen3-8b (forked Qwen3-8B) — SAME for both legs |
| Scenario split | split.json seed=7, 24 train / 10 eval — SAME for both legs |
| Eval grader | hud_env_v2._grade_v2 (cat .35 / mech .20 / kw .25 / ruled_out .10 / rem .10) |
| Eval metric | mean v2 reward on the 10 held-out eval scenarios |
| Data pool | opensre-traj/out/hud_trajectories.jsonl (197 graded trajectories) |

RFT leg: rolls out on the 24 train scenarios, graded by the v2 grader; GRPO group=6, 30 steps,
lr 1e-5, reset_head. (configs/rft.yaml, opensre-traj/train_rft_v2.py)
SFT leg: clones the argmax-reward demo per train scenario (reward >= 0.5). Coverage 21/24
(87.5%); 3 hard scenarios have no qualifying demo and are dropped. Teacher mix: Opus 8, Haiku 7,
Kimi 6. (configs/sft.yaml, train_sft.py, sft_pairs.jsonl)

## 3. Hypotheses (pre-registered)
- H1 (primary): SFT yields the larger single-jump gain (cheap transfer of strong demos).
- H2: RFT yields a smaller additional gain concentrated in mechanism_match.
- H0/failure modes: SFT wins by style-cloning a biased teacher; RFT "wins" via keyword-density
  inflation (hack diagnostic); SFT capped on the no-demo tail.

## 4. Offline proxy ceiling (RAN — not a trained result)
Grading the best held-out demo per eval scenario with the v2 grader gives an upper bound on what
cloning these demos could achieve:

| Metric | Value |
|---|---|
| mean proxy_ceiling_v2 (10 eval scenarios) | 0.6787 |
| mean root_cause_category | 0.700 |
| mean mechanism_match | 1.000 |
| mean evidence_keywords | 0.827 |
| mean ruled_out_red_herrings | 0.268 |
| mean remediation_tool | 0.000 |

Reading: even the BEST demos score ~0.68 — remediation_tool ~0 (demos rarely name the exact fix
tool) and ruled_out_red_herrings is weak (0.27). There is real headroom on those two terms that
RFT could push but SFT cannot exceed (it can only clone what the demos already do). This is the
quantitative basis for H2.

## 5. Trained results (TO FILL — blocked, see 07/09)
| Leg | base | final eval reward | gain | mechanism_match | req_kw_density | winner |
|---|---|---|---|---|---|---|
| SFT | — | — | — | — | — | — |
| RFT | — | — | — | — | — | — |

Fill via: python3 compare_harness.py --rft-log <log> --sft-log <log> --base <base_eval>

## 6. Blocker
The training legs require .venv-hud (3.12) + a forked Qwen slug + HUD Tinker credits. Additionally
the SFT leg is SDK-blocked: hud.TrainingClient is rollout-batch oriented
(step(batch_of_Runs, lr, group_size)) and exposes no supervised token-target step (train_sft.py
introspects and raises a precise NotImplementedError). A true SFT leg needs either a Tinker
supervised endpoint or an out-of-band HF/PEFT SFT on the same sft_pairs.jsonl, then eval through
the same v2 grader. Documented honestly rather than faked.
