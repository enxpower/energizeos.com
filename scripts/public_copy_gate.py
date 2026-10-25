#!/usr/bin/env python3
"""Fail closed on internal process language in customer-facing English website copy."""

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re

# These are high-confidence editorial leaks, not ordinary engineering terms.
PRIVATE_PROCESS = [
    r"\badvertising inventory\b",
    r"\binternal (?:business-development|sales leads|commercial actions)\b",
    r"\bbusiness-development instructions\b",
    r"\b(?:machine-generated|unreviewed)\s+(?:brief(?:ing)?s?|articles?|reports?)\b",
    r"\bautomated\s+(?:market|weekly)\s+(?:brief(?:ing)?s?|reports?|news articles?)\b",
    r"\bad-serving script\b",
    r"\b(?:CI passed|CI failed|pull request|PR #[0-9]+|VWS|handoff prompt|owner approval)\b",
    r"\bAdSense\s+(?:approval|application|readiness|review)\b",
    r"\b(?:our editorial rule|editorial boundary|not republished news articles)\b",
]
PRIVATE_RE = re.compile("|".join("(?:%s)" % value for value in PRIVATE_PROCESS), re.I)
NON_ENGLISH_RE = re.compile(r"[\u3400-\u9fff]")


class PublicText(HTMLParser):
    """Inspect visible text, title/description/accessibility labels and HTML comments."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden_depth = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.hidden_depth += 1
            return
        for key, value in attrs:
            if key in ("alt", "aria-label", "title") and value:
                self.parts.append(value)
            if tag == "meta" and key == "content" and value:
                self.parts.append(value)

    def handle_endtag(self, tag):
        if tag in ("script", "style") and self.hidden_depth:
            self.hidden_depth -= 1

    def handle_data(self, data):
        if not self.hidden_depth and data.strip():
            self.parts.append(data)

    def handle_comment(self, data):
        if data.strip():
            self.parts.append(data)


def check_markup(contents, label):
    parser = PublicText()
    parser.feed(contents)
    problems = []
    for part in parser.parts:
        match = PRIVATE_RE.search(part)
        if match:
            problems.append("Internal process language: " + repr(match.group(0)))
        if NON_ENGLISH_RE.search(part):
            problems.append("Non-English CJK text in public copy")
    if problems:
        return [label + ": " + problem for problem in sorted(set(problems))]
    return []


def self_test():
    allowed = (
        "<html><head><style>/* CI passed is private code, not site copy */</style></head>"
        "<body>Fiber links can show internal reflection and internal resistance. "
        "All results depend on measured connector losses."
        "<script>const status = 'VWS';</script></body></html>"
    )
    assert not check_markup(allowed, "allowed")
    for bad in (
        "<p>Unreviewed machine-generated reports are outside advertising inventory.</p>",
        "<meta name='description' content='PR #52 is waiting for approval'>",
        "<p>Our editorial rule excludes internal business-development instructions.</p>",
        "<!-- Deployment note: VWS has been updated -->",
        "<h1>\u5185\u90e8\u8ba8\u8bba</h1>",
    ):
        assert check_markup(bad, "bad"), "Leak was not rejected: " + bad
    print("PUBLIC_COPY_GATE_SELF_TEST=PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", help="Root directory of the generated public site")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.root:
        parser.error("A public-site root is required")
    root = Path(args.root)
    if not root.is_dir():
        raise SystemExit("PUBLIC_COPY_GATE=FAIL missing public output root: " + str(root))
    html_files = sorted(root.rglob("*.html"))
    if not html_files:
        raise SystemExit("PUBLIC_COPY_GATE=FAIL no HTML pages discovered")
    errors = []
    for path in html_files:
        errors.extend(check_markup(path.read_text(encoding="utf-8"), str(path)))
    if errors:
        for error in errors:
            print("PUBLIC_COPY_GATE=FAIL " + error)
        raise SystemExit(1)
    print("PUBLIC_COPY_GATE=PASS pages=" + str(len(html_files)))


if __name__ == "__main__":
    main()
