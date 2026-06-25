# J7 — 02 Grill (5 personas × 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take

**SMR:** Pointing a frozen LLM at the bench is the right framing, but "the agent" must
be a *policy* with a defined action space and a deterministic reward, or it's a demo, not
an eval. Reuse the registry's gold `fix` as the reward signal — that's already RLVR.

**PSRE:** The bench's whole value is the *live 5-signal chain* (metric→alert→CRE→action→
recovery). If you only score "did the agent name the right kubectl command," you've thrown
away the part that catches a fix that *looks* right but doesn't actually drive the metric
back under SLO. The gcp results prove this: several scenarios had `action_fired=true` but
`recovered=false` (reward 0). A paper-only action-selection score will over-report.

**AAAI:** What's the baseline and the chance rate? 15 actions → random is 1/15 ≈ 0.067.
If you report a single accuracy with no spread and no comparison, a reviewer rejects it.
Also: presenting the gold fix verbatim in the menu is contamination — the model can string-
match the service name. Quantify how much of the score is that artifact.

**RLE:** Action space design matters. Multiple-choice over the 15 gold fixes is a clean
*first* env, but it's trivially gameable (service name appears in both prompt and fix).
The honest version is free-form command generation graded by the live cluster. Since the
cluster is the blocker, ship the MC version but say so loudly.

**DVO:** Confirm the blocker before writing a line of harness: is the temp GCP account
alive? If `gcloud projects list` fails, the live loop is dead and every "live" claim is
fiction. And do NOT fall back to a personal billed account to "make it run."

## Round 2 — react to another persona (genuine disagreement)

**PSRE → SMR:** I disagree that "registry fix = reward" is sufficient. The registry fix is
the reward for the *deterministic* runbook. For an *agent*, the reward must be the metric
recovery on the cluster, because an agent can pick a plausible-but-wrong command. Your
score will look great and mean little. (Accept the critique partially — see R3.)

**SMR → AAAI:** I push back on calling the menu "contamination." It's a defined discrete
action space — that's a legitimate RL formulation (Atari gives you the button set too).
The fair fix is to *report chance rate and a lexical baseline* so the LLM's lift is
visible, not to ban the action set.

**RLE → DVO:** Agree the blocker check comes first, but disagree it makes the task
worthless. A correct offline harness + an honest blocker is exactly the brief's preferred
outcome. The harness is the durable artifact; the cluster is rentable later.

**AAAI → PSRE:** You're right that action-selection ≠ recovery, but a reviewer will *also*
accept a clearly-scoped action-selection eval IF it states it does not measure execution
success. The sin is conflating the two. Label the metric `action_select_accuracy`, not
`reward`, and keep them distinct.

**DVO → RLE:** Fine, but the harness must *record* the chosen command and explicitly mark
`cloud_applied=false` per row, so nobody downstream mistakes a dry-run for a live pass.

## Round 3 — synthesis

Consensus:
1. Build the agent-as-action-selector runner now; it's the durable artifact (RLE, DVO).
2. Check the cloud blocker FIRST; never use a billed personal account (DVO, all).
3. Name the metric `action_select_accuracy` and keep it **separate** from the live
   `reward`/recovery chain — do not over-claim (PSRE, AAAI).
4. Report **chance rate (1/15)** and a **deterministic lexical baseline** so the score is
   interpretable, and flag the menu-leakage caveat honestly (AAAI, SMR).
5. Record each chosen command with `cloud_applied=false`; the live apply is the documented
   blocked step (DVO, PSRE).
