# 02 — Grill (5 personas × 3 rounds)

Personas: Senior ML Researcher (SMR), Principal SRE (PSRE), AAAI Reviewer (AAAI),
RL Engineer (RLE), DevOps Lead (DOL).

## Round 1 — initial take
- **SMR:** FIREBALL is a genuine multi-turn trajectory dataset with structured
  state — good for code-as-policy. Map each turn to (obs, action, result, target).
  The `after_utterances` is the gold continuation; that's our supervision signal.
- **PSRE:** This is a D&D dataset, not SRE. Why is it in an SRE-Degrees repo? It
  only makes sense as a *generic trajectory* substrate to test our converter and
  trajectory schema, not as an incident source. Be explicit about that.
- **AAAI:** Provenance and license matter. Cite the ACL 2023 paper + arXiv id,
  note CC-BY-4.0, and never fabricate rows. If you can't download the full set,
  say so — a documented blocker is publishable; fabricated data is misconduct.
- **RLE:** I care about the action space. Avrae commands (`!cast`, `!attack`) are
  the actions. We should extract verbs as a "tools_used" list so it lines up with
  our SRE tool-call trajectories. Keep raw commands too.
- **DOL:** 1475 files, 100K–1M rows. Do NOT `snapshot_download` the whole repo in
  a worker. Fetch a couple shards. Make `--all` opt-in and loud.

## Round 2 — react to another persona (genuine disagreement)
- **PSRE → SMR:** You called `after_utterances` "the gold continuation." Disagree
  in part: it's often empty (DM narration sometimes lags a turn). If you train on
  it naively you'll get blank targets. You MUST skip empty-target rows.
- **SMR → PSRE:** Pushing back on "why is this here" — the value isn't D&D, it's
  that FIREBALL is one of the few public datasets with *interleaved natural
  language + structured state + executed commands + deterministic results*. That
  is structurally identical to an SRE agent: observe state, issue tool calls, get
  tool output, narrate. It's a clean second substrate. Your empty-target point is
  right though; I concede the skip filter.
- **RLE → DOL:** Agree on size, but disagree that "a couple shards" is enough for
  anything real — for the *converter* it's plenty, but document that a real
  training run needs `--all`. Don't let "validated on 1 shard" imply "dataset
  acquired in full."
- **DOL → AAAI:** You want full provenance, but symlinking the HF cache into an
  out dir (what the fetch does) can confuse reproducibility — a reviewer re-running
  gets a different cache path. Fine for a worker, but note it.
- **AAAI → RLE:** Extracting only the verb loses the target/level args (`-l 5`).
  Keep the full normalized command in `actions`; `tools_used` is a convenience
  view, not the action itself. Don't let the lossy view become the training input.

## Round 3 — synthesis
- Converter keeps BOTH the full `commands_norm` (as `actions`, the real action)
  and a deduped verb list (`tools_used`, convenience). [RLE+AAAI]
- Skip rows with empty action OR empty target by default; `--keep-empty` to
  override. [PSRE+SMR]
- Frame FIREBALL explicitly as a *generic trajectory substrate*, not an SRE
  incident source. [PSRE+SMR]
- Fetch is shard-limited by default, `--all` loud and opt-in; document that full
  training needs all shards. [DOL+RLE]
- Cite paper, arXiv, license; never fabricate; fixture is clearly SYNTH_*. [AAAI]
- Note the symlink/cache reproducibility caveat. [DOL+AAAI]
