#!/usr/bin/env python3
"""Lint a task card so that "done" means "provable".

A card is only useful if every acceptance criterion names a command a machine can
run. This checks the card's shape, not its judgement: it cannot tell whether a
command is the right one, only whether one is there.

Pure standard library, no model calls, no network, Python 3.9+.
Exit codes: 0 compliant, 1 violations on stdout, 2 usage or unreadable file.
"""

import re
import sys

REQUIRED_SECTIONS = ("Goal", "Decisions", "Spec", "Risks", "Acceptance", "Boundaries")

HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$")
# A criterion is any list item in the acceptance section, numbered or bulleted,
# at any indent. Matching only top-level "N." items leaves a hole: a bullet
# appended after two good criteria escapes the command/expectation checks while
# the section still looks compliant.
CRITERION_RE = re.compile(r"^\s*(?:\d+\.|[-*+])\s+(.*)$")
ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\S")
COMMAND_RE = re.compile(r"`[^`]+`")
# "expected" or "期望" as a whole word. Both boundaries matter: without the left
# one "unexpected" counts as an expectation and a criterion saying "unexpected
# output" passes the check it should fail; without the right one "expectedly"
# does the same. The boundaries are ASCII-only and scoped to the English branch
# on purpose — CJK characters are \w, so a blanket \w boundary would reject
# "期望退出码" and even "结果为期望".
EXPECTED_RE = re.compile(r"(?i)(?:(?<!\w)expected(?![a-z])|期望)")


def _sections(text):
    """Return {lowercased heading: [body lines]} for a markdown document."""
    sections = {}
    current = None
    for line in text.splitlines():
        match = HEADING_RE.match(line)
        if match:
            current = match.group(1).strip().lower()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _body(sections, name):
    """Body lines of a required section, or None when the heading is absent."""
    return sections.get(name.lower())


def _criteria(acceptance_lines):
    """Text of every list item in the acceptance section (`1. ...` or `- ...`)."""
    return [m.group(1) for m in map(CRITERION_RE.match, acceptance_lines) if m]


def _has_item(lines):
    return any(ITEM_RE.match(line) for line in lines)


def lint(text):
    """Return (exit_code, violations) for the markdown text of a task card."""
    sections = _sections(text)
    problems = []

    for name in REQUIRED_SECTIONS:
        if _body(sections, name) is None:
            problems.append("missing section: %s" % name)

    acceptance = _body(sections, "Acceptance") or []
    criteria = _criteria(acceptance)
    if len(criteria) < 2:
        problems.append(
            "Acceptance needs at least 2 criteria (found %d)" % len(criteria)
        )
    for number, criterion in enumerate(criteria, 1):
        if not COMMAND_RE.search(criterion):
            problems.append("criterion %d: no backticked command" % number)
        if not EXPECTED_RE.search(criterion):
            problems.append("criterion %d: missing Expected/expected" % number)

    risks = _body(sections, "Risks")
    if risks is not None and not _has_item(risks):
        problems.append("missing section: Risks")

    if problems:
        return 1, problems
    return 0, []


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        sys.stderr.write("usage: card_lint.py <card.md>\n")
        return 2
    path = argv[0]
    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        # A file we cannot decode is a file we cannot check: that is exit 2,
        # not a violation. Letting the UnicodeDecodeError escape would report
        # exit 1 and claim the card is non-compliant when it was never read.
        sys.stderr.write("cannot read %s: %s\n" % (path, exc))
        return 2

    code, problems = lint(text)
    if code == 0:
        print("OK")
    else:
        for problem in problems:
            print(problem)
    return code


if __name__ == "__main__":
    sys.exit(main())
