# D14 — 02 Grill (5 personas x 3 rounds)

Personas: **SMR** Senior ML Researcher · **PSRE** Principal SRE · **AAAI** AAAI Reviewer ·
**RLE** RL Engineer · **DVO** DevOps Lead.

## Round 1 — initial take

**SMR:** Scaling the RFT task set from 10 to 42 is the right move — 10 tasks is far below
the threshold where GRPO advantage estimates stop being dominated by per-task difficulty.
But "42" must be 42 *distinct* learning signals, not 34 + 8 near-duplicates of the same
class. If the 8 variants are trivially close to their canonical parent, you've added 8
tasks of effective rank ~0.

**PSRE:** From an incident-response view, the 19 real postmortem incidents (101-119) are
worth 10x the synthetic ones — they encode the *misleading-symptom* structure that breaks
naive responders (DNS "fix" that corrupts zone files, etc.). I want the 42-set to *keep
all 19 reals*, not dilute them with synthetic variants. Variants of `001-oom_kill` teach
nothing a real on-call cares about.

**AAAI:** Define "benchmark" precisely. If the paper claims "trained on the 42-incident
benchmark," a reviewer will ask: is 42 the *eval* set too? Training and evaluating on the
same 42 is a leakage red flag. State the train/eval split or you'll get desk-rejected.

**RLE:** The mechanical risk: `train_rft_v2.py` selects tasks by integer index into
`Taskset.from_module`, which only enumerates the 34 canonical ids. If 8 of your 42 are
variants, they are **unreachable by index**. Your launcher MUST construct tasks from
explicit scenario_ids, or "42" silently collapses to 34.

**DVO:** Nobody's mentioned that the open-model backend needs a forked Qwen slug and
`.venv-hud`. The config can be perfect and still 404 on `models/resolve`. The deliverable
has to degrade gracefully: dry-run that proves correctness offline, smoke that proves the
pipeline, and a documented backend prerequisite.

## Round 2 — react to another persona BY NAME (forced disagreement)

**PSRE → SMR:** I disagree with SMR's "42 must be 42 distinct signals." For RFT you
*want* within-class variance — the 8 perturbed variants of synthetic bases are exactly the
GRPO group-diversity SMR claims to want elsewhere. Identical signals are bad; *near*
signals with different evidence framings are how the policy learns the invariant. Don't
strip them.

**SMR → PSRE:** And I disagree with PSRE's "drop synthetic variants, keep only reals."
You can't GRPO 19 tasks into a stable head — 19 is still small, and the reals are
*harder* (difficulty 4-5), so early training sees almost no positive reward signal.
Synthetic difficulty-3 incidents are the curriculum floor. Remove them and the policy
never gets off the ground. Keep all 34 canonical + variants.

**RLE → AAAI:** AAAI's leakage worry is real but mis-scoped here. This task is *deliver
the RFT training set*, not the eval protocol. The 42 are the **training** task set;
pass@k eval already exists separately (`rex/eval_pass_at_k.py`). Conflating the two would
over-engineer D14. Note the split exists; don't build it.

**AAAI → RLE:** I'll push back: "eval exists separately" is not an excuse to ship a task
file with no `kind`/`origin` provenance. If I can't tell from the artifact which tasks are
real vs synthetic, canonical vs variant, I can't audit contamination. The task file MUST
carry that metadata even if the split logic lives elsewhere.

**DVO → SMR:** SMR keeps optimizing the task mix while ignoring that *the run won't start*
without a forked model. A beautiful 42-task curriculum that 404s is worth zero. Priority
order: runnable scaffold + dry-run proof first, mix-tuning second.

## Round 3 — synthesis

Consensus reached:
1. **Keep all 34 canonical (15 synthetic + 19 real) + 8 hard variants = 42.** This
   satisfies PSRE (all 19 reals kept), SMR (synthetic difficulty-3 floor kept; variants
   add within-class spread), and hits exactly 42. (RLE/SMR disagreement resolved: keep both.)
2. **Build tasks from explicit scenario_ids, not indices** (RLE) — non-negotiable, else 42
   collapses to 34.
3. **Task file carries provenance** `kind` (canonical/variant) + `origin`
   (real_postmortem/synthetic) + `difficulty` + `category` (AAAI) so contamination is
   auditable; train/eval split is out of scope but the metadata enables it.
4. **Graceful degradation** (DVO): offline `--dry-run` proves config + id resolution;
   `--smoke` proves the rollout->reward->step pipeline; the forked-slug requirement is a
   documented backend prerequisite, not a code defect.
5. **Curriculum by real difficulty** (SMR) — order easy->hard so early steps get reward.
