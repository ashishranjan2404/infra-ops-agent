#!/usr/bin/env python3
"""Validate the F13 conference poster artifacts (stdlib only).

Checks:
  - poster.md contains all required sections.
  - poster.html is well-formed (tag stack balances, ignoring void elements).
  - poster.html carries the print/poster CSS (@page, @media print, size: A0).
  - no placeholder tokens (lorem / TODO / FIXME) in either file.
  - cited [src: ...] repo paths that point at real files actually exist.

Exit 0 iff zero errors.
"""
import os
import re
import sys
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))  # -> /Users/mei/rl
MD = os.path.join(HERE, "poster.md")
HTML = os.path.join(HERE, "poster.html")

REQUIRED_SECTIONS = ["Motivation", "Method", "Benchmark", "Results", "Takeaways"]
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr"}
PLACEHOLDERS = ["lorem", "todo", "fixme", "xxxx"]


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


class StackParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass  # self-closing, balanced

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"closing </{tag}> with empty stack")
            return
        if self.stack[-1] != tag:
            # tolerate optional-close by searching back
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.errors.append(
                        f"implicitly-unclosed <{self.stack[-1]}> before </{tag}>")
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
            else:
                self.errors.append(f"stray </{tag}> (top was <{self.stack[-1]}>)")
        else:
            self.stack.pop()


def check_markdown(text):
    errs = []
    low = text.lower()
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in low:
            errs.append(f"poster.md missing required section: {sec}")
    return errs


def check_html_wellformed(text):
    p = StackParser()
    p.feed(text)
    errs = list(p.errors)
    if p.stack:
        errs.append("unclosed tags at EOF: " + ", ".join(p.stack))
    return errs


def check_print_css(text):
    errs = []
    needles = ["@page", "@media print", "size:a0", "size: a0"]
    low = text.lower()
    if "@page" not in low:
        errs.append("poster.html missing @page rule")
    if "@media print" not in low:
        errs.append("poster.html missing @media print")
    if "size:a0" not in low and "size: a0" not in low:
        errs.append("poster.html missing 'size: A0' page sizing")
    for sec in REQUIRED_SECTIONS:
        if sec.lower() not in low:
            errs.append(f"poster.html missing section heading text: {sec}")
    return errs


def check_no_placeholder(name, text):
    errs = []
    low = text.lower()
    for tok in PLACEHOLDERS:
        if tok in low:
            errs.append(f"{name} contains placeholder token: {tok!r}")
    return errs


def check_sources_exist(md_text):
    """Every [src: ...] path that looks like a repo file must exist."""
    errs = []
    cited = set()
    for blob in re.findall(r"\[src:([^\]]+)\]", md_text):
        for part in blob.split("·"):  # middot separators
            for token in re.split(r"[\s,&]+", part.strip()):
                token = token.strip()
                # only treat as a path if it has a slash or a file extension
                if "/" in token and re.search(r"\.[a-z]{1,5}$", token):
                    cited.add(token)
    for path in sorted(cited):
        if not os.path.exists(os.path.join(REPO, path)):
            errs.append(f"cited source does not exist: {path}")
    return errs, sorted(cited)


def main():
    md = read(MD)
    html = read(HTML)
    errors = []
    errors += check_markdown(md)
    errors += check_html_wellformed(html)
    errors += check_print_css(html)
    errors += check_no_placeholder("poster.md", md)
    errors += check_no_placeholder("poster.html", html)
    src_errs, cited = check_sources_exist(md)
    errors += src_errs

    print("=== F13 poster validation ===")
    print(f"repo root: {REPO}")
    print(f"required sections present (md): "
          f"{[s for s in REQUIRED_SECTIONS if s.lower() in md.lower()]}")
    print(f"cited repo file-paths checked: {cited}")
    if errors:
        print(f"\nFAIL ({len(errors)} error(s)):")
        for e in errors:
            print("  - " + e)
        return 1
    print("\nPASS: poster.md + poster.html valid, well-formed, print-styled, sources exist.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
