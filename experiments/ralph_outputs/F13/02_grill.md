# 02 — Grill (Ralph Loop: 5 personas, 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE),
**REV** (AAAI Reviewer), **RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial take

- **SMR:** A poster is a marketing surface, but the science still has to survive a 90-second
  read. Lead with the *thesis* ("a real cascade misleads frontier models on the first try")
  and the *reward formula* — those are the defensible IP. Put the frontier lift table front
  and center.
- **PSRE:** The thing that makes this credible to operators is the **trap**: the loudest
  alert is on the victim, and the naive fix (scale the crash-looping control plane) makes it
  worse. If the poster doesn't show a concrete cascade example, SREs won't believe it's real.
- **REV:** The first question I write on the review form is "is the headline lift an
  artifact?" Your own `headline_insights.md` says the REx lift was mostly **oracle-feedback
  leakage** (REx 0.25 ≈ zero-shot 0.24 with the hint stripped). If the poster shows +0.23
  lift and hides that, it's a desk-reject for integrity. Show the ablation.
- **RLE:** Numbers must be reproducible from one command. Put `python3 -m rex.frontier` and
  the reward formula on the poster so a reader can rerun it. Also: "within-group reward
  spread (0.0/0.15/1.0)" is the RL-relevant claim — that's why the data trains, say it.
- **DVO:** It has to actually print. A0 at 300dpi, CMYK-safe colors, no reliance on a web
  font that won't embed, and it must open offline (self-contained HTML). I've seen too many
  posters render as a blank page at the print shop.

## Round 2 — react to another persona by name (genuine disagreement)

- **REV → SMR:** I disagree with SMR putting the frontier lift table "front and center" as
  the hero. That table (0.63→0.86 etc.) is the *optimistic* read. If it's the biggest thing
  on the poster and the ablation is a footnote, you've inverted the honesty hierarchy. The
  hero should be the **environment + searched verifier** — the parts the ablation *didn't*
  knock down. Make REx's lift a secondary, caveated panel.
- **SMR → REV:** Partly disagree back. A poster that leads with "our headline result is
  mostly leakage" is scientifically pure but nobody stops walking. The frontier table is a
  legitimate *demo* result (frozen models, real reward, real escalation behavior) — it's not
  fraudulent, it's a different claim than the ablation. Solution isn't to bury it; it's to
  **label** it precisely: "REx as deployment wrapper converges 5 frozen models to the 0.86
  safe ceiling" — and put the ablation caveat *adjacent*, same size, not hidden.
- **PSRE → RLE:** I push back on RLE's "one command reproduces it." On the **real GKE tier**
  it does *not* reproduce from one command — it needs a live cluster, Prometheus, the mesh
  deployed. The poster should be explicit about the **two-tier contract**: Tier-A sim is the
  one-command reproducible part; Tier-B is "validated, not one-click." Conflating them is the
  kind of overclaim a hostile SRE reviewer eats alive.
- **RLE → PSRE:** Fair, but don't over-hedge into uselessness. The *mechanism* claim is what
  Tier-B validates ("faulting one node propagates to a downstream victim on real GKE"); the
  *numbers* are Tier-A. State exactly that sentence from ARCHITECTURE.md and we're covered.
- **DVO → SMR:** SMR keeps talking content; I'll keep saying it won't matter if the file is
  3 columns of text at 11px that nobody reads from 2 meters. Disagreement: **cut ~40% of the
  words.** A poster is not a paper. Big numbers, one cascade diagram, the formula, the table,
  five takeaways. If a sentence isn't on a slide-worthy claim, it's QR-code material.

## Round 3 — synthesis

Consensus the poster will follow:

1. **Honesty hierarchy (REV + SMR resolution):** Frontier lift table and the ablation caveat
   appear at the **same visual weight**, adjacent. Frontier is labeled as the *deployment-
   wrapper demo* claim; ablation is labeled as the *rigor* claim. The genuine, un-knocked-down
   contributions (verifiable env + searched self-generalizing verifier) get the hero panel.
2. **Concreteness (PSRE):** One worked cascade example panel — loud alert on victim, hidden
   root cause, trap, correct fix — drawn from a real reconstructed outage.
3. **Reproducibility + two-tier honesty (RLE + PSRE):** Reward formula + `python3 -m
   rex.frontier` printed; explicit two-tier contract box (sim = one-command; GKE = mechanism-
   validated).
4. **RL claim (RLE):** State within-group reward spread as the reason the data trains.
5. **Printability (DVO):** A0 portrait, self-contained HTML, embedded/system fonts only,
   ~40% fewer words than a paper, `@page size:A0`, `@media print`. Big hero numbers.
