#!/usr/bin/env python3
"""Structural validator for the AAAI paper package (no TeX toolchain required).

Checks, across main.tex and all \\input-ed section files:
  1. Every \\begin{env} has a matching \\end{env} (balanced, correctly nested).
  2. Braces { } are balanced (ignoring escaped \\{ \\} and comment lines).
  3. Every \\input{...} target exists on disk.
  4. The document has the AAAI-required spine: documentclass[letterpaper]{article},
     \\begin{document}..\\end{document}, \\maketitle, abstract, and a bibliography.

Exit code 0 = all checks pass; 1 = at least one failure.
"""
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def strip_comments(line: str) -> str:
    # Remove TeX comments: a % not preceded by a backslash starts a comment.
    out, i, n = [], 0, len(line)
    while i < n:
        c = line[i]
        if c == "\\" and i + 1 < n:
            out.append(line[i : i + 2])
            i += 2
            continue
        if c == "%":
            break
        out.append(c)
        i += 1
    return "".join(out)


def read_clean(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return "\n".join(strip_comments(ln) for ln in f)


def gather_files(main_path: str):
    """Return [main] + all \\input-ed files (relative to ROOT)."""
    files, missing = [main_path], []
    text = read_clean(main_path)
    for m in re.finditer(r"\\input\{([^}]+)\}", text):
        target = m.group(1)
        if not target.endswith(".tex"):
            target += ".tex"
        p = os.path.join(ROOT, target)
        if os.path.exists(p):
            files.append(p)
        else:
            missing.append(target)
    return files, missing


def check_environments(text: str):
    stack, errors = [], []
    for m in re.finditer(r"\\(begin|end)\{([^}]+)\}", text):
        kind, env = m.group(1), m.group(2)
        if kind == "begin":
            stack.append(env)
        else:
            if not stack:
                errors.append(f"\\end{{{env}}} with no open environment")
            elif stack[-1] != env:
                errors.append(f"\\end{{{env}}} but innermost open is \\begin{{{stack[-1]}}}")
                stack.pop()
            else:
                stack.pop()
    for env in stack:
        errors.append(f"\\begin{{{env}}} never closed")
    return errors


def check_braces(text: str):
    depth = 0
    t = text.replace("\\{", "").replace("\\}", "")
    for ch in t:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return ["unbalanced: extra closing brace }"]
    if depth != 0:
        return [f"unbalanced braces: net depth {depth:+d}"]
    return []


def main() -> int:
    main_path = os.path.join(ROOT, "main.tex")
    if not os.path.exists(main_path):
        print("FAIL: main.tex not found")
        return 1

    files, missing = gather_files(main_path)
    ok = True

    print("== \\input targets ==")
    if missing:
        ok = False
        for t in missing:
            print(f"  FAIL: missing \\input target {t}")
    else:
        print(f"  PASS: all {len(files) - 1} \\input targets exist")

    combined = "\n".join(read_clean(p) for p in files)

    print("== environment balance ==")
    env_err = check_environments(combined)
    if env_err:
        ok = False
        for e in env_err:
            print(f"  FAIL: {e}")
    else:
        print("  PASS: all \\begin/\\end environments balanced and nested")

    print("== brace balance (per file) ==")
    for p in files:
        errs = check_braces(read_clean(p))
        rel = os.path.relpath(p, ROOT)
        if errs:
            ok = False
            for e in errs:
                print(f"  FAIL: {rel}: {e}")
        else:
            print(f"  PASS: {rel}")

    print("== AAAI required spine ==")
    spine = {
        r"\documentclass[letterpaper]{article}": r"\\documentclass\[letterpaper\]\{article\}",
        r"\begin{document}": r"\\begin\{document\}",
        r"\end{document}": r"\\end\{document\}",
        r"\maketitle": r"\\maketitle",
        "abstract env": r"\\begin\{abstract\}",
        "bibliography": r"\\bibliography\{",
    }
    main_text = read_clean(main_path)
    for label, pat in spine.items():
        if re.search(pat, main_text):
            print(f"  PASS: {label}")
        else:
            ok = False
            print(f"  FAIL: missing {label}")

    print()
    print("RESULT:", "ALL CHECKS PASS" if ok else "FAILURES PRESENT")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
