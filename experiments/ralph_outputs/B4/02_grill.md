# B4 — Ralph Loop Grill (5 personas, 3 rounds)

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PSRE)**, **AAAI Reviewer (REV)**,
**RL Engineer (RLE)**, **DevOps Lead (DOL)**.

## Round 1 — initial takes

**SMR:** The deliverable is a stratification of an *already-computed* metric. The intellectual
content is the **classifier**, not the table renderer. If the type labels are noisy, all three
tables are noise. I want the classifier to be deterministic and auditable, and I want to see
the **per-type within-group reward spread** in each table — a type with std≈0 is untrainable and
that's the headline finding, not pass@1.

**PSRE:** "simple / cascade / novel" must mean something operationally. Simple = root is the
alerting node (leaf, root visible). Cascade = root is buried under downstream SLO breaches.
Novel = a failure mode the agent has not seen the *mechanism* of (leap-second, zk split-brain).
If the classifier just trusts `registry.json` it inherits whoever labelled that — I want a
fallback that reads `assertions.cascades` and SLO-node count so the label is grounded in the
scenario mechanics, not a string.

**REV:** Three tables split a fixed N into thirds → each cell's CI balloons. If novel has n=10
and pass@1=0.1, the Wilson CI is enormous. The paper claim "REx helps most on novel" is only
defensible if I show CIs and ideally a between-type contrast. Don't oversell per-type pass@1
point estimates. Also: is the type assignment leaking? If "novel" was defined *post hoc* by
which incidents the model failed, that's circular.

**RLE:** Reuse `experiments/compute_pass_at_k.py` as the single estimator source — do NOT
re-implement pass@k with a different formula in the renderer, or the B4 tables won't match A1.
Pull the numbers straight from the result JSON's `by_family` block (which A1 already computed
with the canonical estimator) rather than recomputing from raw passes — recomputing risks drift.

**DOL:** Whatever script I run must be re-runnable and not touch shared state. It should
discover result files itself (glob), tolerate missing/partial files, and never write outside
B4/artifacts. If a new model run lands tomorrow I want to re-run and get updated tables for free.

## Round 2 — react to another persona (genuine disagreement)

**RLE → SMR:** I disagree with SMR that the renderer is trivial "table printing." If I pull
A1's pre-computed `by_family` numbers (RLE-R1 position) then the renderer really *is* trivial
and that's the *correct, low-risk* choice — recomputing to "add value" is how you get tables
that silently disagree with the published A1 result. The value-add is the **classifier covering
the 19 unlabelled incidents**, full stop. SMR is over-weighting the renderer.

**SMR → RLE:** Then we partly agree, but you're wrong that pulling A1's block is sufficient.
A1 only ran 42 incidents; the *corpus* is 51. If B4 claims to "stratify the generated set" while
silently dropping 19 incidents, that's a coverage lie. The renderer must show which incidents
are classified-but-unevaluated, or a reviewer (REV) eats us alive.

**PSRE → REV:** I push back on REV's "novel is circular" worry. Novelty here is **not** defined
by model failure — A8 defined held-out by *training-set token/company overlap* and the 80-89
series are dated real outages (Knight Capital 2012, FB BGP 2021) with mechanisms absent from the
synthetic train set. That's a *provenance-based* novelty label, set before any eval. Not circular.

**REV → PSRE:** Provenance helps, but "novel" and "cascade" are not mutually exclusive —
facebook_bgp_backbone is *both* a cascade *and* novel. A single 3-way label forces a false choice.
I'd accept a **primary-type** label (novelty dominates when present, else cascade-vs-simple by
mechanics) but the doc MUST state that ordering rule explicitly or the tables are ambiguous.

**DOL → RLE:** Agree on glob-discovery, but disagree with "tolerate partials silently" — the
`.json.partial` ablation file is *incomplete by definition*. If I fold it into the tables I get
numbers that change every time the partial grows. Either exclude `.partial` or label it clearly
as provisional. I'll exclude it from headline tables.

## Round 3 — synthesis

Consensus:
1. **Classifier is the deliverable.** Renderer pulls pre-computed `by_family` numbers from
   result JSONs (RLE) — no re-estimation, guaranteeing parity with A1/A2.
2. **Cover all 51.** registry.json/A8 label 32; deterministic fallback labels the other 19.
   Show classified-but-unevaluated incidents explicitly (SMR/REV coverage honesty).
3. **Primary-type ordering rule (REV):** `novel` (provenance: A8 held-out OR dated real outage)
   wins; else `cascade` if `assertions.cascades` AND >1 SLO node; else `simple`. State it in spec.
4. **Each table reports Wilson CI + reward_std** (REV CIs, SMR trainability spread).
5. **Cross-check** our classifier vs each result's `incidents_by_family`; emit a mismatch report
   (don't silently trust either side).
6. **Exclude `.partial`** from headline tables, list it as provisional (DOL).
7. Single estimator source = `compute_pass_at_k.py` (only used if we ever recompute; default is
   to read pre-computed blocks).
