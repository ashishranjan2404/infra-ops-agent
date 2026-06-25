# F8 · 10 Feedback for the next task

Grounding a governance/meta deliverable in *measured* repo facts (not the project's own
docs) paid off twice: parsing the committed `hud_trajectories.jsonl` revealed 197
rollouts across 3 models — contradicting the stale DATA.md — and `git status` exposed
the 53 `scenarios/cidg/generated/*.yaml` as untracked, a real fresh-clone gap. Two
reusable lessons: (1) make any checklist *self-auditing* with a tiny stdlib script that
checks claims against the live repo (path/import/`git ls-files`/grep + one genuine
behavioral check), so reviewers can re-run it rather than trust prose — and keep a
single generator for both the human doc and the machine manifest to avoid the
count-drift smell I hit. (2) For a frozen/sampled-LLM system, never write a flat
"reproducible": split **replay** (committed transcripts + deterministic judge = exact)
from **generation** (mean ± std over seeds, not bitwise), and pin *which judge and
seed* backs each number — that judge-to-result linkage is the thing still missing
repo-wide and is the highest-value next fix. The brief's no-touch rule on shared core
files is easy to honor by writing fixes as documented recommendations (commit the
scenarios / refresh DATA.md) rather than applying them.
