#!/usr/bin/env python3
"""H2 — validate the eval-ci workflow YAML parses and has the required shape.

Run locally or as a pre-flight before copying eval-ci.yml into .github/workflows/.
Exit 0 = valid, 1 = invalid. Pure stdlib + pyyaml; no network.
"""
from __future__ import annotations

import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
WORKFLOW = os.path.join(HERE, "eval-ci.yml")


def main() -> int:
    with open(WORKFLOW) as fh:
        doc = yaml.safe_load(fh)

    errors: list[str] = []
    if not isinstance(doc, dict):
        print("FAIL: workflow did not parse to a mapping", file=sys.stderr)
        return 1

    if doc.get("name") != "eval-ci":
        errors.append(f"name should be 'eval-ci', got {doc.get('name')!r}")

    # YAML 1.1 parses the bare key `on:` as boolean True via PyYAML.
    triggers = doc.get("on", doc.get(True))
    if not isinstance(triggers, dict) or "pull_request" not in triggers:
        errors.append("missing pull_request trigger (PR gating is the whole point)")

    jobs = doc.get("jobs", {})
    if "eval-suite" not in jobs:
        errors.append("missing 'eval-suite' job")
    else:
        steps = jobs["eval-suite"].get("steps", [])
        runs = " ".join(str(s.get("run", "")) for s in steps)
        if "pytest" not in runs:
            errors.append("no pytest invocation found in eval-suite steps")
        if "passk_smoke.py" not in runs:
            errors.append("no pass@k smoke invocation found in eval-suite steps")

    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK: {WORKFLOW} is a valid eval-ci workflow "
          f"(PR trigger + pytest + pass@k smoke present)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
