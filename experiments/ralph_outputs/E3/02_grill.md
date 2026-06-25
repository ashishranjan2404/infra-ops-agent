# E3 — 02 Grill (5 personas × 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (AAAI)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial take
- **SMR:** A 3-way comparison where one arm has no model is really a 2-way comparison with
  an annotation. Fine — but make the zero-shot arm the *exact same base model* the OpenSRE
  arm was trained from, or the comparison measures model identity, not training.
- **PSRE:** Cascades are the only incidents that matter here — loud alert ≠ root cause, naive
  fix worsens it. 14 of them is a reasonable stress set. Make sure "pass" requires clearing
  the *root*, not just silencing the loudest alert.
- **AAAI:** With 14 incidents and a couple of seeds you have ~28 trials/arm. Report Wilson CIs
  and do NOT claim significance on a 3-point pass@1 gap. State the effect size and overlap.
- **RLE:** The OpenSRE run was flat in prior logs. If you show a null result, that's a *finding*,
  not a failure. Just don't bury it. Use the deterministic judge so it's reproducible.
- **DOL:** Don't touch `agent/models.py` — other Ralph workers are running. Register slugs locally.
  And probe reachability before burning a 60-job sweep.

## Round 2 — react to another persona BY NAME (genuine disagreement)
- **SMR → PSRE:** I disagree with PSRE's "14 is reasonable" hand-wave. 14 cascades at 2 seeds
  is *underpowered* to separate two arms ~3 points apart. We should either accept it's
  descriptive (no significance claims) or raise seeds. I'd rather be honest about power than
  pretend 28 trials settles it.
- **PSRE → AAAI:** AAAI wants more seeds, but more seeds on a frozen flat model just shrinks the
  CI around "no difference." That's *not* worth the gateway cost. I'd rather spend budget making
  sure the scoring actually rewards root-cause fixes than chasing tighter CIs on a null.
- **AAAI → RLE:** RLE says "null is a finding" — agreed, but only if the harness is *capable* of
  showing a non-null. If the judge is so strict that base Qwen-8B scores ~0 on every cascade,
  then OpenSRE "no lift" is uninformative (floor effect). We need to confirm there's headroom:
  base must score meaningfully above 0 and below 1 on this set.
- **RLE → DOL:** DOL's "probe first" is right, but probing isn't enough — a slug can return 200
  yet be the *wrong* checkpoint. I want the harness to record the exact `model` string per arm
  in the result so the comparison is auditable, not just a label.
- **DOL → SMR:** SMR wants strict apples-to-apples base==OpenSRE-base. I agree, but the base
  Qwen3-8B on the gateway may have been served with different sampling defaults than the forked
  slug. We can't fully control that from here; document it as a caveat rather than claim perfect
  control.

## Round 3 — synthesis
Consensus:
1. **Honest 2-way** (zero-shot vs OpenSRE) + a **documented blocked Fireball arm**; never fabricate.
2. **Same base model** for zero-shot as OpenSRE was forked from (`Qwen/Qwen3-8B`), with a caveat
   that gateway serving/sampling parity isn't perfectly controllable (DOL/SMR).
3. **Descriptive, not significance-claiming** — report pass@1, Wilson CI, mean, std; explicitly
   note overlapping CIs (SMR/AAAI).
4. **Headroom check** (AAAI/RLE): confirm base scores strictly between floor and ceiling on this
   set so a null lift is interpretable, not a floor effect — the per-incident means + reward std
   in the output serve this.
5. **Auditable** (RLE): record the exact gateway `model` string per arm in the result.
6. **Parallel-safe** (DOL): local roster registration only; probe before the sweep.
