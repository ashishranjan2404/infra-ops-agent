# Data-Sharing / Legal Checklist — Snorkel incident data

Gating list. Nothing in this list goes in the *cold* email; it activates **after**
mutual interest. Each item is a yes/no a human must resolve before data moves.

## Phase 0 — Before any data is requested
- [ ] Confirm internal authority to enter a data agreement (who signs?).
- [ ] Decide the *minimum* viable ask (a few structured records) vs the moonshot
      (open benchmark) — don't request more than we can legally hold.
- [ ] Confirm we will **not** request raw production logs (PII / security risk).
      Request only anonymized, structured incident records or a runnable env.

## Phase 1 — NDA / agreement
- [ ] Mutual NDA executed before any sample data is shared.
- [ ] Data-use agreement scopes: permitted use (research only?), redistribution,
      derived-works (can we publish models trained on it?), term, termination.
- [ ] Clarify whether records are Snorkel-owned or third-party (their clients);
      third-party data may carry additional consent constraints.

## Phase 2 — Anonymization / PII
- [ ] Written confirmation each record is anonymized: no hostnames, internal IPs,
      customer names, employee names, account/ticket IDs, secrets, IaC paths.
- [ ] PII status declared per record (`none` / `redacted` / `present`); reject any
      `present`.
- [ ] Agree a redaction standard (e.g. entities → role placeholders) and a
      spot-check process on our side before ingestion.

## Phase 3 — Licensing & attribution
- [ ] License recorded per record (`source.license` field in the schema).
- [ ] If destined for an **open** benchmark: confirm an open-compatible license
      (CC-BY / CC0 / similar) and required attribution string.
- [ ] Confirm we may cite Snorkel as data partner in the paper (and how they want
      to be named).

## Phase 4 — Security & transfer
- [ ] Secure transfer channel agreed (no email attachments of sensitive data).
- [ ] Storage location + access control on our side defined (who can read it).
- [ ] Note: do **not** commit partner data into the public repo; keep it in a
      gitignored / access-controlled path, ingest only the anonymized normalized
      form.

## Phase 5 — Retention & deletion
- [ ] Retention period agreed; deletion-on-request honored.
- [ ] Deletion procedure defined (including derived caches / training shards).

## Phase 6 — Publication
- [ ] Pre-publication review right for Snorkel if they request it.
- [ ] Honest evidence-class labeling in the paper: partner records are
      **expert-constructed / anonymized**, not raw production incidents (see
      `snorkel_contact_brief.md` §5).

## Sign-off
- [ ] Legal/owner sign-off recorded with date before first ingestion.
