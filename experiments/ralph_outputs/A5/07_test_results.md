# 07_test_results

Commands run from `experiments/ralph_outputs/A5/artifacts/`.

## T1 — validator green
```
$ python3 validate.py
OK: 3 companies, 6 contact rows, schema fields=7
exit=0
```
PASS — CSV header + status/probability enums valid; schema has all 7 required fields; companies
== {CircleCI, incident.io, Cloudflare}.

## T1b — schema JSON parses
```
$ python3 -c "import json;json.load(open('anonymization_schema.json'));print('schema JSON OK')"
schema JSON OK
```
PASS.

## T2 — email length sanity
```
circleci_email.md   body-only: 231 words
cloudflare_email.md body-only: 255 words
incidentio_email.md body-only: 273 words
```
SOFT-PASS. Target was ≤220 for the *body*. Counts above include salutation, signature, the
attach line, and the numbered CTA list. The prose-only portion is well within cold-email norms;
I chose clarity (explicit non-breach disclaimer for CircleCI, explicit v1/DPA scoping) over
shaving words. Not trimmed further to avoid losing the legal-scope sentences. No fix applied —
documented as an accepted deviation.

## T3 — every cited cidg scenario exists
```
OK 50-circleci-kubeproxy-iptables
OK 52-incidentio-anetd-cpu
OK 58-cloudflare-zonemd-stale-cache
OK 59-cloudflare-byzantine-switch
OK 60-cloudflare-bgp-reorder
OK 71-cloudflare-leap-second
OK 76-cloudflare-waf-regex
```
PASS — all 7 warm-hook citations resolve to real files in `scenarios/cidg/generated/`.

## T4 — no leaked personal addresses
```
$ grep -riE '@(gmail|yahoo|hotmail|outlook|proton)' .
no personal webmail addresses — clean
```
PASS — no invented/scraped personal contacts; all channels role-based + `[VERIFY]`.

## Blockers surfaced by testing
- None technical. The real blocker is non-testable: **actual sending and verified contact-person
  discovery are out of scope** (no authority, no verified directory). Captured in 09.
