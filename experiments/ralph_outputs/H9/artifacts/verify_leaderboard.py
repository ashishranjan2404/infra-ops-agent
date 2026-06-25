#!/usr/bin/env python3
"""Verify the H9 leaderboard: JSON is valid, HTML references it, and the page
actually fetches+parses it when served over HTTP.

Run: python3 verify_leaderboard.py
"""
import json
import os
import re
import sys
import http.server
import socketserver
import threading
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(HERE, "leaderboard.json")
HTML_PATH = os.path.join(HERE, "leaderboard.html")

checks = []


def ok(name, cond, detail=""):
    checks.append((name, bool(cond), detail))


# 1. JSON parses and has required schema
with open(JSON_PATH) as f:
    data = json.load(f)
ok("leaderboard.json parses", True)
ok("has entries array", isinstance(data.get("entries"), list) and data["entries"], f"{len(data['entries'])} entries")

required = {"rank", "system", "model", "family", "source", "pass@1", "episodes"}
for e in data["entries"]:
    missing = required - set(e)
    ok(f"entry rank {e.get('rank')} schema", not missing, f"missing={missing}")
    p1 = e.get("pass@1")
    ok(f"entry rank {e.get('rank')} pass@1 in [0,1]", isinstance(p1, (int, float)) and 0 <= p1 <= 1, str(p1))

# 2. Real numbers cross-check against known A1/A2/E3 values
by = {(e["source"], e["system"], e["model"]): e for e in data["entries"]}
expect = {
    ("A1", "REx (tree + oracle feedback)", "glm-5p2"): 0.897,
    ("A1", "zero_shot", "glm-5p2"): 0.230,
    ("A2", "REx (tree + oracle feedback)", "deepseek-v4-pro"): 0.893,
    ("E3", "OpenSRE-trained (GRPO)", "opensre-qwen3-8b"): 0.107,
    ("E3", "zero_shot (base 8B)", "qwen3-8b-base"): 0.071,
}
for key, val in expect.items():
    e = by.get(key)
    ok(f"real number {key[0]}/{key[1]}", e is not None and abs(e["pass@1"] - val) < 1e-3,
       f"expected {val} got {e['pass@1'] if e else None}")

# 3. HTML references leaderboard.json
html = open(HTML_PATH).read()
ok("HTML fetches leaderboard.json", 'fetch("leaderboard.json"' in html or "fetch('leaderboard.json'" in html)
ok("HTML renders entries", "data.entries" in html)

# 4. Live load: serve dir over HTTP, fetch HTML and JSON, confirm both 200 and JSON parses
PORT = 8754
os.chdir(HERE)
handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
t = threading.Thread(target=httpd.serve_forever, daemon=True)
t.start()
try:
    base = f"http://127.0.0.1:{PORT}"
    h = urllib.request.urlopen(base + "/leaderboard.html", timeout=5)
    ok("HTTP serves leaderboard.html (200)", h.status == 200)
    j = urllib.request.urlopen(base + "/leaderboard.json", timeout=5)
    served = json.loads(j.read())
    ok("HTTP serves leaderboard.json and parses", j.status == 200 and len(served["entries"]) == len(data["entries"]))
finally:
    httpd.shutdown()

# Report
fails = [c for c in checks if not c[1]]
for name, passed, detail in checks:
    print(f"[{'PASS' if passed else 'FAIL'}] {name}" + (f"  ({detail})" if detail and not passed else ""))
print(f"\n{len(checks) - len(fails)}/{len(checks)} checks passed")
sys.exit(1 if fails else 0)
