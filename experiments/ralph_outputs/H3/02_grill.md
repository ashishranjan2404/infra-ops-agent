# 02 — Grill (Ralph Loop, 5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer
(AAAI), RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial takes
- **SMR:** "Reproducibility for a paper means *pinning*. A Dockerfile that
  installs `pyyaml>=6` is not reproducible — a rebuild in 6 months pulls a
  different numpy. For the artifact to be defensible you need a lockfile or
  `==` pins, and ideally a recorded base-image digest."
- **PSRE:** "The image must run as non-root and carry no secrets. The eval
  needs `HUD_API_KEY` — that key must be injected at `docker run` time via
  `-e`, never `COPY`'d or `ENV`'d into a layer. Also: a default `docker run`
  should *do something safe and observable*, not crash asking for a key."
- **AAAI:** "What does 'containerize the eval' even validate? If the live eval
  needs a gateway API that reviewers can't reach, the container proves
  nothing at review time. There must be an offline mode that demonstrates the
  *deterministic* core (the part that makes the metric reproducible)."
- **RLE:** "Don't bloat the image with the GPU/SFT stack (unsloth/trl). That's
  `requirements.txt`, not `requirements-rex.txt`. Keep it CPU-only and small,
  or builds take 20 minutes and nobody runs them."
- **DOL:** "Layer caching and `.dockerignore` are the whole game for build
  time. Copy `requirements*` first, install, THEN copy source. Exclude
  `.git`, venvs, `runs/`, `experiments/results/`. And tag the base image —
  `:latest` is an instant audit fail."

## Round 2 — genuine disagreement (react by name)
- **DOL → SMR:** "I disagree with hard `==` pins as the *default*. This is a
  research repo, not a regulated deploy. `==` pins rot and break rebuilds when
  a yanked version disappears from PyPI. Pinning the *base image* and using
  the range from `requirements-rex.txt` is the pragmatic call; a full lock is
  gold-plating for H3's scope."
- **SMR → DOL:** "Partly conceding — but then the README MUST be explicit that
  the image is reproducible *modulo* PyPI dependency drift, or the
  reproducibility claim is dishonest. I won't accept a silent range."
- **AAAI → PSRE:** "I push back on 'default run should be safe' as merely nice.
  It's *load-bearing*. If the default `docker run` needs a secret, a reviewer
  who lacks the key concludes the artifact is broken. The default MUST be the
  offline smoke. This is a correctness requirement, not UX polish."
- **PSRE → AAAI:** "Agreed, and stronger: the offline smoke should exercise
  the *real import graph and real scenario files*, not a toy. A green smoke
  that imports nothing proves nothing — same failure mode you're worried
  about, one level down."
- **RLE → DOL:** "One disagreement: don't `COPY . .` even with a good
  `.dockerignore`. Explicit `COPY agent/ rex/ ...` keeps layers stable and
  the image minimal. `.dockerignore` is a safety net, not the primary tool."

## Round 3 — synthesis
Consensus:
1. Base image **tagged** (`python:3.13-slim`), not `:latest`. (DOL, all)
2. Deps from `requirements-rex.txt` **as-is** (ranges), with the README
   stating reproducibility is *modulo PyPI drift*. (DOL+SMR compromise)
3. **No secrets in image**; `HUD_API_KEY` injected at runtime via `-e`. (PSRE)
4. **Default `docker run` = offline smoke** that imports the real eval modules
   and loads the real bundled scenarios. (AAAI+PSRE — load-bearing)
5. CPU-only; never install the GPU/SFT stack. (RLE)
6. Explicit `COPY` of needed packages + `.dockerignore` as safety net;
   requirements-first layer ordering. (RLE+DOL)
7. Non-root user; exec-form ENTRYPOINT/CMD. (PSRE+DOL)
