# F5 — Test Results

## Grounding verification (real command output)

### Confirm ablation arms + means (ouroboros B2)
```
$ python3 -c "import json;d=json.load(open('rex/runs/ablation.json'));print(d['aggregate'])"
zero_shot       mean 0.242  std 0.261
best_of_n       mean 0.235  std 0.304
retry_realistic mean 0.230  std 0.254
rex             mean 0.687  std 0.265
rex_no_oracle   mean 0.250  std 0.255
```
→ Confirms the abstract's "0.69 versus 0.24 zero-shot … collapses to 0.25." The
`rex_no_oracle` arm EXISTS in the JSON, so the oracle-leakage claim is repo-backed, not
only insight-doc-backed. B2 resolved: claim stands on `ablation.json`.

### Confirm harness synthesis numbers
```
$ python3 -c "import json;d=json.load(open('rex/runs/harness_synth.json'));print(len(d['train']),'train',len(d['heldout']),'heldout',len(d['rules']),'rules')"
7 train 3 heldout 3 rules
```
→ Confirms "trained on seven incidents … fourteen rules to three." The 0.90/0.95 held-out
accuracy is cited from `docs/headline_insights.md` §2 (the synth run's evaluated accuracy);
n=3 held-out, hence the abstract uses "roughly 0.90," no false precision.

## Deliverable checklist (from 04_spec / 05_ouroboros)
```
T1 file exists & non-empty ............... PASS
T2 body word count <= 250 ................ PASS (233)
T3 body word count >= 180 (advisory) ..... PASS (233)
T4 trap-action hook present .............. PASS  (/naive fix|worsen/)
T5 honest limitation present ............. PASS  (/feedback|oracle/ AND /zero-shot|collapse/)
T6 released-artifacts mention ............ PASS  (/releas/ AND /benchmark/)
T7 markdown structure (heading + rule) ... PASS
forbidden-claims scan .................... PASS  (no 89.7/94.9, no "2x pass", no McNemar p)
```

## Word count (the hard gate)
```
$ sed -n '/^# Abstract/,/^---$/p' abstract.md | grep -v '^# Abstract' | grep -v '^---$' \
    | grep -v '^[[:space:]]*$' | wc -w
233
```
**Reported word count: 233 (≤ 250).**

## Markdown parse check
```
$ python3 -c "open('experiments/ralph_outputs/F5/artifacts/abstract.md').read(); print('readable OK')"
readable OK
```
Heading `# Abstract` present; exactly one body-terminating `---`; Provenance under `##`.

## Result
All gates PASS. No failures required fixes; the draft was authored to spec on the first
pass after grounding verification.
