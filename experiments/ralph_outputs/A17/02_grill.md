# A17 — The Grill (Ralph Loop): 5 personas × 3 rounds

Personas: **Senior ML Researcher (SMR)**, **Principal SRE (PS)**, **AAAI Reviewer (AR)**,
**RL Engineer (RLE)**, **DevOps Lead (DL)**.

## Round 1 — initial take

**SMR:** A datasheet is the right move. The critical sections for credibility are
*Composition* and *Collection Process*. The benchmark claims provenance from real
postmortems — the card must make the synthetic-vs-real boundary explicit, or it reads
as overclaiming. I want every count machine-derived.

**PS:** From an SRE standpoint the value proposition is "loudest alert is not the cause"
+ "buried smoking gun." The card should quantify that: how many scenarios actually have
`buried_gun_exists` and `cascades`? If it's not most of them, the headline thesis is weak.
Also: these are all `chaos_kind: exec` on a *simulator*, not real telemetry. Say so loudly.

**AR:** I will check three things: (1) contamination — are these scenarios derived from
public postmortems an LLM may have memorized? (2) construct validity — does solving the
sim correlate with real incident response? (3) license. If the card hand-waves any of
these, I down-score reproducibility.

**RLE:** For RL/eval use I need the *scoring contract* in the card: what's the gold label,
how is a response judged correct, is it deterministic? The reward signal comes from
`gold_root` + `red_herrings` + the deterministic judge. That belongs in the card so
results are reproducible across labs.

**DL:** Reproducibility = pinned versions + seeds + exact file manifest. Each scenario has
a `seed`. Is the sim deterministic given the seed? The card must state the determinism
guarantee and how to regenerate the corpus, or "reproducible" is a lie.

## Round 2 — react to another persona by name (force disagreement)

**AR → SMR:** I disagree that making the synthetic/real boundary "explicit" is enough.
You're treating provenance as a labeling problem. The deeper issue is **contamination**:
scenarios 70–82 are literally titled "Facebook 2021-10-04 BGP backbone withdrawal",
"Knight Capital", "Cloudbleed". Any frontier LLM has read those postmortems. The card
must warn that high scores on *named* scenarios may reflect memorization, not diagnosis.
A boundary note doesn't fix that — a contamination *risk* section does.

**PS → RLE:** I push back on your "just document the judge" framing. The judge is a
**substring/keyword** matcher (`_hit_counts` over `gold_root`/`red_herrings`). That's
fragile — an agent can hit the gold keywords without understanding the mechanism, and a
correct paraphrase can miss them. Documenting it isn't sufficient; the card must call the
keyword judge a *known threat to validity*, not just a contract.

**DL → PS:** I disagree that "all sims, not telemetry" is purely a weakness to confess.
It's also the reproducibility *feature*: a deterministic simulator with seeds is exactly
why other labs can reproduce numbers, which real telemetry never allows. The card should
frame it as a deliberate trade-off (external validity ↓, reproducibility ↑), not an apology.

**SMR → AR:** Partial disagreement. Contamination matters, but you over-index on the named
scenarios. Half the corpus (40–47, 20–22, 30) are synthetic *leaf* templates with no
real-world title — those are contamination-safe. The card should **split the composition
by provenance class** (synthetic-leaf vs postmortem-derived) so a reader can compute a
contamination-controlled subset. That's more useful than a blanket warning.

**RLE → DL:** I agree on seeds but you're missing that determinism of the *sim* ≠
determinism of the *eval*. The default judge can fall back to an **LLM judge** (see
`default_judge` in `rex/scoring.py`). If a lab uses the LLM-judge path, results are NOT
deterministic. The card must specify which judge to use for reproducible numbers
(deterministic/hybrid) vs. which introduces nondeterminism.

## Round 3 — synthesis

Consensus action items for the card:
1. **Machine-derive every number** (SMR, all) — ship `compute_stats.py`; paste its output.
2. **Split composition by provenance class** (SMR): synthetic-leaf vs postmortem-derived,
   so readers can build a contamination-controlled subset.
3. **Dedicated contamination-risk section** (AR): named historical incidents may be
   memorized; recommend reporting leaf-subset scores separately.
4. **Quantify the thesis** (PS): report `cascades` and `buried_gun_exists` counts; these
   are the construct the benchmark tests.
5. **Document the scoring contract AND its threats** (RLE+PS): keyword judge is the
   reproducible default; note paraphrase/keyword-hacking fragility; specify that the
   LLM-judge fallback breaks determinism.
6. **Frame sim+seed as a reproducibility trade-off** (DL), not just a limitation; state
   the determinism guarantee and how to regenerate.
7. **Be honest about empty `meta.urls`** and the registry(32)/disk(35) gap.
