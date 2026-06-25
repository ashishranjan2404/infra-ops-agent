# A18 — 02 Grill (5 personas, 3 rounds)

Personas: **SMR** (Senior ML Researcher), **PSRE** (Principal SRE), **AAAI** (AAAI Reviewer),
**RLE** (RL Engineer), **DVO** (DevOps Lead).

## Round 1 — initial take

**SMR:** A dataset card is only as good as its schema. The 197 records have heterogeneous fields
(real records carry `difficulty`/`source_company`/`source_url`/`trap_actions`; synthetic don't). If
the loader infers types it'll choke or null-pun. Declare an explicit `Features` schema and default-fill.

**PSRE:** The whole *value* of this dataset is the real-outage provenance. Every real record MUST keep
its `source_url` to a first-party postmortem, and `trap_actions` must survive the round-trip. If the
upload drops those, it's just another synthetic toy set. Validate provenance explicitly.

**AAAI:** Reproducibility and licensing. Apache-2.0 is fine for code-derived data, but the card needs a
**Limitations & Ethics** section: these are reconstructed simulations of real outages, not raw
production telemetry. Reviewers will reject a dataset that implies it's real captured data.

**RLE:** The selling point is the **model spanning set** giving within-group reward spread (the GRPO
signal). The card must show the per-model leaderboard so a consumer knows the difficulty is legible.
Also expose `subscores` so people can re-weight the reward.

**DVO:** Make the push idempotent and credential-safe. Use `exist_ok=True`, read the token from env,
and ship a `--dry-run` so CI can validate without secrets. No hardcoded tokens, ever.

## Round 2 — react to another persona (genuine disagreement)

**RLE → SMR:** I disagree that we even *need* a loading script. `datasets>=2` reads a bare JSONL with a
`configs:` block in the card. A custom script is extra surface area that can break on the Hub's
sandboxed loader. Just ship JSONL + card.

**SMR → RLE:** No. A bare JSONL means `datasets` *infers* the schema, and with real-only fields present
on only 114/197 rows you get fragile auto-typing and silent nulls. The script's whole point is a
**stable typed contract**. I'll concede your safety concern by ALSO making the card self-sufficient
(`configs:` + `dataset_info:`) so the dataset still resolves even if the script is ignored — but the
script stays.

**AAAI → PSRE:** You're overselling provenance. A `source_url` doesn't make a trajectory *correct* — the
agent's `answer` is still a frozen-LLM guess scored by an automatic proxy grader. Don't let the card
imply these are gold human labels.

**PSRE → AAAI:** Fair hit. Provenance is about the *incident*, not the *answer*. The card should say the
URL grounds the scenario's ground truth, while the trajectory + reward are model output + auto-score.
I accept adding that distinction.

**DVO → RLE:** Even if we skip the script, we can't skip splitting the JSONL into `synthetic/` and
`real/` shards — the card's `synthetic`/`real` configs need files to point at. So the push step must
*build* the package, not just copy one file. That's non-negotiable for the multi-config card to work.

**RLE → DVO:** Conceded — if we keep multi-config, we need the shards. (Or drop multi-config. I'd keep it;
the real/synthetic split is the most useful slice.)

## Round 3 — synthesis

Consensus:
1. **Keep the loading script** (typed schema, default-fill real-only fields) **and** make the card
   self-sufficient with `configs:` + `dataset_info:` — belt and suspenders (SMR + RLE).
2. **Build, don't copy**: push script assembles root JSONL + `synthetic/` + `real/` shards (DVO).
3. **Provenance section** distinguishes grounded *incident* vs auto-scored *trajectory* (PSRE + AAAI).
4. **Leaderboard + subscores** in the card so difficulty/reward are legible and re-weightable (RLE).
5. **Limitations & Ethics**: reconstructed simulation, automatic proxy reward, small frozen-LLM set
   (AAAI).
6. **Credential-safe push**: env token, `exist_ok`, `--dry-run`, no secrets in code (DVO).
