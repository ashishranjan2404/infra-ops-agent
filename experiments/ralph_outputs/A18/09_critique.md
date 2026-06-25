# A18 — 09 Critique (honest)

## What's weak / what a reviewer attacks
1. **Pushed to a personal namespace, not an org.** The dataset went to `quantranger/...` (the only
   identity the local token authorizes for write). A reviewer wants a stable org repo
   (e.g. an `SRE-Degrees` org) and a curated card review before public release. Re-targeting is a
   one-arg change (`--repo-id`) but the *current* live repo is personal.

2. **Pre-existing cruft in the live repo.** The target repo already contained unrelated `rex/*.jsonl`
   files from a prior push; `upload_folder` adds/overwrites but does not delete them. The published repo
   is therefore slightly messier than the package I built. A `delete_patterns=` or fresh repo would fix
   it; I did not delete others' files to stay conservative.

3. **`dataset_info` feature schema is hand-mirrored.** The card's `all`-config feature list is maintained
   by hand to match the loader's `Features`. If one drifts, the Hub shows a card warning. There's no
   automated single-source-of-truth generation (e.g. emitting the YAML from the loader). Acceptable for a
   197-row static set, but fragile if the schema evolves.

4. **Auto reward, not gold labels.** The dataset is frozen-LLM answers scored by a deterministic proxy
   grader. It is excellent for *eval/GRPO signal* but is **not** a human-validated RCA gold set; the card
   says so, but a careless consumer could still over-trust the `reward` field.

5. **Small model spanning set (3 models).** Within-group spread exists but is thin; an AAAI reviewer
   would want more models / seeds for statistically robust difficulty calibration.

6. **`trap_actions` shipped but ungraded.** The trap-fix penalty grader is deferred, so the most
   interesting signal (did the agent take the harmful naive fix?) is present as data but not yet a
   reward component.

## What's missing
- No automated Hub-side card-validation CI (the `datasets-server` viewer check).
- No `LICENSE` file copied alongside (the YAML declares apache-2.0 but no license text file is shipped).
- No dataset versioning/tag on the Hub commit.

## Honest status
The *deliverable* — a validated, loadable, properly-metadata'd HF dataset package — is real and
complete, and it is live on the Hub. The caveats above are about **publication polish and namespace**,
not about whether the package works. Nothing was faked: every count, the leaderboard, and the live
load-back are from the actual 197 records.
