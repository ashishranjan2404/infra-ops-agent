# D1 — 03 Improved Plan (post-grill)

## What changed vs 01
1. **Analyzer now emits a falsifiable verdict.** Per AAAI/SMR, `analyze_curve.py`
   reports the OLS slope *and* classifies the run as `continuing-up` / `flat` /
   `reversed-down` against a `--flat-eps` threshold (default 0.005/step). A naked
   "+0.037" is no longer the claim; the verdict is.
2. **Launcher is background + append-only + resumable.** Per DOL, `run_rft_50.sh`
   writes to an append-only JSONL and is documented as "run unattended"; it relies
   on the retry wrapper already in `train_rft_v2.py`. A mid-run 5xx no longer loses
   prior steps.
3. **Hyper-params frozen to the 15-step run** (group 6, lr 1e-5, tasks 0–9). Per
   RLE/SMR, this keeps the 50-step curve composable with the existing 15-step one.
4. **reward_std surfaced** so the PSRE proxy concern is visible, without a reward
   redesign (kept out of D1 scope).

## Critiques accepted
- AAAI "no naked delta": accepted — analyzer reports slope + verdict; SUMMARY notes
  the slope is small relative to per-step std (~0.18), i.e. likely within noise.
- DOL "background + append-only": accepted — core to the launcher design.
- RLE/SMR "freeze hyper-params": accepted.

## Critiques rejected (with reason)
- AAAI "need ≥3 seeds before any claim": **rejected for D1.** The brief asks for a
  runnable 50-step config + partial curve under a tight compute cap, not a
  publication. Multi-seed is the correct *next* task, recorded in 10_feedback. We
  instead make the single-run claim honest (slope + noise band) rather than
  multiplying GPU cost beyond the cap.
- PSRE "redesign reward to track MTTR before more steps": **rejected for D1.** v2's
  P0 deterministic mechanism score is already the chosen objective; redesigning it
  is a different task. We only *log* reward_std to keep the concern visible.

## Net plan
Reuse `train_rft_v2.py` unmodified; add a 50-step wrapper, a verdict-emitting
analyzer, a live smoke, and a real background 50-step run capped at ~15 min of
attended time — capturing the real partial curve and documenting the compute
blocker if 50 steps don't complete.
