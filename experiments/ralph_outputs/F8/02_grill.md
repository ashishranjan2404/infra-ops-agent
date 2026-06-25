# F8 · 02 Grill — 5 personas × 3 rounds

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DOL** DevOps Lead.

## Round 1 — initial takes

**SMR**: A reproducibility checklist for a *frozen-LLM, code-as-policy* system is
unusual. The headline truth most reviewers miss: with sampled API models the
**outputs are not bit-reproducible**, only the harness control flow is. The checklist
must say that loudly or it's misleading. Seeds in `rex/tree.py` only fix the
Thompson-sampling tree shape, not what the LLM returns.

**PSRE**: From an ops angle, "reproducible" also means *re-runnable on a clean box*.
Two requirements files (`requirements.txt` GPU stack vs `requirements-rex.txt`
runtime) is good hygiene but a fresh cloner will trip over it. The checklist should
prescribe the exact happy-path: `pip install -r requirements-rex.txt`, set keys,
run `rex.eval_pass_at_k`. Also: the scenarios under `scenarios/cidg/generated/` are
**untracked** — that's a dead repro on a fresh clone.

**AAAI**: I want the standard NeurIPS checklist items answered with Yes/No/Partial +
*where*. Vague "we provide code" gets flagged. Also need: license, compute budget,
number of seeds, error bars, and a statement on closed-model versioning. If a number
in the paper can't be regenerated, say so in the limitations.

**RLE**: The seeding story is real but partial. `eval_pass_at_k.py` and `ablation.py`
take `--seeds`/`SEEDS=3`. But the **judge** matters: `scoring.py` has a
`deterministic_judge` (fully reproducible) AND an `_llm_judge`/`hybrid_judge` (NOT).
Which judge produced the paper numbers? The checklist must pin the judge per result.

**DOL**: Pin everything: Python 3.13.7, git SHA, and the API model version strings
(`agent/models.py` has `claude-haiku-4-5-20251001`, `gpt-5.5`, etc.). Without the
dated model string the "model" is a moving target. Also secrets handling: `.env`
has `ANTHROPIC_API_KEY`, `FIREWORKS_API_KEY`, `EXA_API_KEY` — checklist must say keys
are required and NOT committed.

## Round 2 — react to another persona (genuine disagreement)

**SMR → RLE**: I disagree with RLE's framing that pinning the judge "fixes"
reproducibility. Even with the `deterministic_judge`, the *input* to the judge (the
LLM's stated cause) is stochastic, so pass@k will vary run to run. Pinning the judge
makes *grading* reproducible given a transcript, but not the end-to-end metric.
We must distinguish **transcript-level** repro (replay a saved `.jsonl`, fully
deterministic) from **generation-level** repro (re-run the model, NOT deterministic).
The checklist needs both rows.

**RLE → SMR**: Partially concede, but you're overstating it. With temperature-0 /
`no_temperature` reasoning models the variance is small, and we run **multiple seeds
with error bars** precisely to make the claim statistical, not bitwise. Demanding
bitwise repro of an API model is a category error — no one can do that. The honest
bar is: *committed transcripts replay exactly*, and *fresh generations reproduce the
reported means within the stated CI*. I'll insist the checklist phrase it that way,
not as a flat "not reproducible."

**PSRE → DOL**: I push back on DOL's "pin the dated model string and you're fine."
Pinning `claude-haiku-4-5-20251001` does not guarantee the provider serves identical
weights forever — providers silently patch. The only durable artifact is the
**committed trajectory dataset** (`opensre-traj/out/hud_trajectories.jsonl`). The
checklist should rank the committed `.jsonl` as the primary reproducibility anchor and
treat live re-generation as best-effort.

**AAAI → PSRE**: I disagree that the committed `.jsonl` is sufficient. DATA.md says
only the *Claude half* (60 rollouts) is committed and the glm/minimax half is
"pending (teammate), rate-limited." A reviewer cannot reproduce a table that depends
on data not in the repo. That's a **PARTIAL/BLOCKED**, not a green check. Don't let
the existence of *some* data launder the missing data.

**DOL → AAAI**: Fair, but I disagree with treating untracked generated scenarios as
fatal. They're *generated* — if the generator script and its seed are committed, the
data is reproducible-by-construction even if the YAML isn't checked in. The right fix
is to commit either the artifacts **or** the deterministic generator + seed. The
checklist should flag which of the two we actually have.

## Round 3 — synthesis

Consensus the checklist must encode:
1. **Two reproducibility tiers**, stated explicitly:
   - *Transcript/replay tier* — committed `.jsonl` + `deterministic_judge` → fully
     deterministic, AVAILABLE.
   - *Generation tier* — re-running API/open models → reproducible only in
     distribution (means ± CI over seeds), NOT bitwise. Mark SEEDED-CONTROL-FLOW.
2. **Per-result judge pinning** — record which judge (`deterministic` vs
   `llm`/`hybrid`) backs each metric (`scoring.py`).
3. **Data honesty** — committed Claude-half trajectories = AVAILABLE; glm/minimax
   half = BLOCKED (rate-limit); the 53 `scenarios/cidg/generated/*.yaml` = PARTIAL
   (present on disk, **untracked in git** → not on a fresh clone). Recommend committing
   the artifacts OR the generator+seed.
4. **Weights** — closed models: version-string-pinned, NOT weight-reproducible
   (inherent). Open training (`train_rft.py`): reproducible *recipe* but BLOCKED on
   HUD_API_KEY + GPU; no checkpoint committed.
5. **Environment** — Python 3.13.7, git SHA, `requirements-rex.txt` (runtime) vs
   `requirements.txt` (GPU). Keys required, not committed.
6. A **self-audit script** so the checklist is mechanically checkable, not just prose.

Rejected: AAAI's implicit "untracked data = whole thing fails" — softened to PARTIAL
because a committed deterministic generator can substitute (DOL's point), pending which
one actually exists. Rejected: DOL's "dated model string ⇒ reproducible weights" — PSRE
correct that providers drift; demoted to "best-effort, committed transcripts are primary."
