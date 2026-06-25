# 02 — Grill (5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**,
**AAAI Reviewer (REV)**, **RL Engineer (RLE)**, **DevOps Lead (DL)**.

## Round 1 — initial takes
- **SMR:** A Makefile is fine but it must encode the *reproducibility contract*.
  The eval target should default to the deterministic-judge path, not an
  LLM-judge, so `make eval` is reproducible. Otherwise the "convenience" wrapper
  silently hides nondeterminism.
- **PSRE:** I care about blast radius. `make clean` that `rm -rf`s the wrong
  thing is a classic foot-gun. And targets that spend money (gateway calls) must
  be impossible to trigger by accident — at minimum loudly documented.
- **REV:** If this Makefile is a paper artifact, the targets must map 1:1 to the
  claims. A reviewer running `make eval-smoke` then `make figures` should
  reproduce the headline. Hidden flags = irreproducible.
- **RLE:** `train` is special — it needs `.venv-hud` (py3.12) and a *forked*
  Qwen slug, not a generic model name. If the Makefile pretends train is "just
  another target" with the same PYTHON, it will fail confusingly.
- **DL:** `.PHONY`, a `.DEFAULT_GOAL := help`, and override-via-variable are
  table stakes. Also: where does the Makefile live? If it's in an artifacts dir
  it must still find the repo root, or it's useless to anyone who copies it.

## Round 2 — react to another persona (genuine disagreement)
- **RLE → SMR:** I disagree that `make eval` should *only* ever be deterministic.
  The frontier sweep is a real, cited experiment too. Forcing one blessed path
  hides half the project. Better: default deterministic, but expose
  `eval-frontier` as a first-class sibling — don't bury it behind a flag.
- **PSRE → DL:** "table stakes" is doing a lot of work. Your tidy `.PHONY`
  Makefile still let me write `clean: rm -rf $(REPO)/...`. The dangerous part
  isn't missing phony decls, it's the recipe. I want `clean` scoped to
  `__pycache__` ONLY and explicitly excluding `.venv*`. Cosmetics ≠ safety.
- **REV → RLE:** You're overcomplicating `train`. For an *artifact*, a train
  target that requires a hand-forked slug and a live GPU provider is not
  reproducible anyway — so don't pretend it is. I'd rather have a `train-smoke`
  that fails fast and is honestly labeled "needs HUD_API_KEY + forked slug" than
  a heavyweight `train` that looks runnable but isn't.
- **SMR → REV:** Pushing back — dropping `train` entirely because it's not
  one-command-reproducible is wrong. The *command* is the artifact even when the
  *result* needs infra. A documented, correct train invocation has value: it
  tells the reader exactly how the open model was trained. Keep both train and
  train-smoke; label the infra dependency.
- **DL → PSRE:** Fair on `clean`. Conceding: I'll scope it and exclude venvs.
  But I still insist on the ergonomics (help, phony, overrides) — they're not
  mutually exclusive with safety, and a Makefile no one can read is its own
  reliability risk.

## Round 3 — synthesis
Consensus reached:
1. **Reproducible-by-default eval** (deterministic judge, `glm-5p2`, explicit
   per-family/seeds) AND a first-class `eval-frontier` sibling + `eval-smoke`
   fast path. (SMR + RLE)
2. **Safe `clean`**: `__pycache__` only, `-not -path './.venv*/*'`, `|| true`.
   (PSRE + DL)
3. **train + train-smoke** both shipped, both clearly marked "needs HUD_API_KEY,
   `.venv-hud`, forked Qwen slug"; train-smoke is the fail-fast path. (SMR + RLE
   + REV compromise)
4. **Self-locating repo root** so the Makefile works from the artifacts dir.
   (DL)
5. **1:1 target↔command mapping**, validated by `make -n` on every target so a
   reviewer sees exactly what runs. (REV)
