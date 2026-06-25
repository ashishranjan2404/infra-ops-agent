# 02 — Grill (Ralph Loop: 5 personas × 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **REV** (AAAI
Reviewer), **RLE** (RL Engineer), **DOL** (DevOps Lead).

## Round 1 — initial take

**SMR:** A Related Work section is judged on *positioning*, not on listing papers. The
must-haves: REx (we literally implement its Thompson-tree), CWM (our sim is a world
model), and the RLVR line (our reward is the contribution). The trap is describing a
paper inaccurately — reviewers Google every cite.

**PSRE:** From the ops side, the section has to make clear we are *not* re-doing SREGym.
SREGym is a live-cluster benchmark; we're a training loop on a cheap sim with explicit
trap labels. If a reader leaves thinking "this is SREGym minus a cluster," we failed.

**REV:** I'll attack two things: (1) citations to "AutoHarness" and "REx" — are these
*real, canonical* papers or names your codebase invented? If the latter, you must phrase
them as "the AutoHarness-style synthesis line" and anchor to *real* test-synthesis work,
or I flag it as a phantom citation. (2) Any claim of statistical rigor must name the
exact tests (McNemar, Wilson) — vague "we use significance testing" is a red flag.

**RLE:** The RLVR positioning has to be precise. GRPO is DeepSeekMath/R1. RLVR-as-a-term
is Tülu-3-ish. Don't conflate them. And the *deterministic reward* angle is the actual
novelty — contrast it explicitly against LLM-as-judge (Zheng/MT-Bench), or the
contribution reads as "we used GRPO like everyone else."

**DOL:** Keep it readable. A wall of 30 citations with no through-line is useless. I want
a summary table mapping each thread → what we borrow → what's new. Make the *delta*
scannable.

## Round 2 — react to another persona BY NAME (genuine disagreement)

**REV → SMR (disagree):** SMR says "positioning over listing," fine — but SMR is too
relaxed about the phantom-citation risk. I *insist*: if "AutoHarness" and "REx" are not
verifiable published papers under those exact titles, citing them as `[Author, Year]`
with a fabricated venue is worse than not citing. I'd rather see "we follow the
harness-synthesis paradigm (cf. search-based test generation, TestGen-LLM)" than a fake
DOI. This is a hard line.

**SMR → REV (partial pushback):** I disagree that we should strip the names. The
*codebase itself* names AutoHarness and REx in module docstrings — that's the framing the
authors chose. Erasing them loses the through-line. Compromise: keep the names as the
*paradigm label*, attach the real underlying mechanism, and DON'T invent a venue we're
unsure of. Name + accurate mechanism + conservative attribution.

**RLE → PSRE (disagree):** PSRE wants the section centered on the SRE/benchmark contrast.
I think that's the *least* novel axis — every applied-RL paper has a "we're not just a
benchmark" paragraph. The reviewer cares more about whether our *reward* and *transfer*
claims are defensible. Weight the section toward §2.4–2.6, not §2.1.

**PSRE → RLE (rebut):** Disagree. If the SRE framing is weak, the whole paper is "GRPO
on a toy sim." The credibility comes from the incidents being real postmortems and the
traps being real ops mistakes (restart CoreDNS during kube-proxy failure, etc.). The
benchmark contrast IS load-bearing — it's what makes a sim believable. Keep §2.1 strong.

**DOL → REV (agree-then-extend):** REV's phantom-citation rule is right, but I'd operationalize
it: the validator should *require the citation strings to be present* but the human (us)
guarantees accuracy by describing mechanism, not metrics. A script can't verify a DOI is
real; it CAN verify we didn't silently drop CWM or Constitutional AI.

## Round 3 — synthesis

Consensus reached:
1. **Keep AutoHarness/REx as paradigm labels** (the repo uses them), attach the *real
   mechanism*, and anchor to verifiable underlying work (search-based test gen / bandit
   refinement) — conservative on exact venue. (SMR + REV compromise.)
2. **Balance the section:** strong §2.1 SRE-benchmark contrast (PSRE) *and* a
   reward/transfer-heavy back half (RLE). Both load-bearing.
3. **No fabricated DOIs/venues** where uncertain; describe by mechanism (REV hard line).
4. **Deterministic-reward vs LLM-judge** is the headline novelty in the RLVR para (RLE).
5. **Summary table** for scannability (DOL).
6. **Name exact statistical tests** (REV).
7. Validator enforces *citation coverage + structure*, not metric correctness (DOL).
