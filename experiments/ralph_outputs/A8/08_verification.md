# A8 — 08 Verification (against success criteria)

| Success criterion (from 01) | Met? | Evidence |
|---|---|---|
| Manifest lists held-out incident ids | ✅ | `heldout_manifest.json.held_out` = 15 keys; `heldout_split.csv` all 32 rows |
| Manifest states the novelty criteria | ✅ | `manifest.criteria` (tier1/tier2/tier3 + stop & company token lists + strict_class_mode) |
| Guard exits 0 on held-out set | ✅ | T3: exit 0, "PASS: zero overlap" |
| Guard exits 1 on a known contaminated id | ✅ | T4 negative control: exit 1, 4 violations listed |
| No shared core file edited | ✅ | only files written are under `experiments/ralph_outputs/A8/` (git status confirms) |

## Are the outputs real (not placeholder)?
- **Yes.** `training_stats` is computed from the actual 268 trajectory lines:
  34 distinct training incidents, derived live. The held-out list is the output of
  the classifier over the real registry, not hand-written.
- The manifest carries a content `sha256` (3c8b7ee2…) over canonical JSON so any
  tampering is detectable.
- Independent re-derivation: the guard recomputes the training set from raw jsonl
  rather than trusting the manifest, and still passes.

## Strictness sanity
- Every `cascade` incident (14) is correctly excluded — they are public
  post-mortems from companies present in training.
- The held-out set spans two families (8 simple synthetic + 7 novel real-world
  incidents whose source orgs — facebook, knight capital, azure, firefox, gke,
  kafka — are absent from training), so it is not a trivial single-family set.

Verification: **PASS.** Deliverable meets all stated success criteria with real,
re-runnable artifacts.
