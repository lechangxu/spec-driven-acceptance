"""Unit tests for card_lint.

Behavioural tests call `card_lint.lint()` directly; only the two exit-code tests go
through the command line, because exit codes live in `main()`.
"""

import os
import subprocess
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import card_lint  # noqa: E402  (path setup must happen first)

EXAMPLE = os.path.join(ROOT, "examples", "task-card.example.md")

GOOD_CARD = (
    "## Goal\n\nSomething small.\n\n"
    "## Decisions\n\n1. Keep it boring.\n\n"
    "## Spec\n\nThe tool filters by tag.\n\n"
    "## Risks\n\n- Tags may be misspelled -> criterion 1.\n\n"
    "## Acceptance\n\n"
    "1. `grep -q '^\\[x\\]' todos.txt` -> Expected exit 0\n\n"
    "2. `test -s todos.txt` -> Expected exit 0\n\n"
    "## Boundaries\n\n- Do not touch storage.\n"
)


def lint_text(text):
    return card_lint.lint(text)


def replace(text, old, new):
    assert old in text, "fixture drift: %r not found" % old
    return text.replace(old, new, 1)


class CardLintTest(unittest.TestCase):
    def test_example_passes(self):
        with open(EXAMPLE, encoding="utf-8") as handle:
            code, problems = lint_text(handle.read())
        self.assertEqual((0, []), (code, problems))

    def test_missing_section(self):
        card = replace(GOOD_CARD, "## Spec\n\nThe tool filters by tag.\n\n", "")
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertIn("missing section: Spec", problems)

    def test_too_few_criteria(self):
        card = replace(
            GOOD_CARD,
            "2. `test -s todos.txt` -> Expected exit 0\n\n",
            "",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertTrue(any("at least 2" in p for p in problems), problems)

    def test_missing_command(self):
        card = replace(
            GOOD_CARD,
            "1. `grep -q '^\\[x\\]' todos.txt` -> Expected exit 0\n\n",
            "1. The list still prints -> Expected exit 0\n\n",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertTrue(any("no backticked command" in p for p in problems), problems)
        # A bulleted criterion is a criterion too: it cannot slip past the checks.
        card = replace(
            GOOD_CARD,
            "2. `test -s todos.txt` -> Expected exit 0\n\n",
            "2. `test -s todos.txt` -> Expected exit 0\n\n"
            "- the list still prints -> Expected exit 0\n\n",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertTrue(any("no backticked command" in p for p in problems), problems)

    def test_missing_expected(self):
        card = replace(
            GOOD_CARD,
            "1. `grep -q '^\\[x\\]' todos.txt` -> Expected exit 0\n\n",
            "1. `grep -q '^\\[x\\]' todos.txt`\n\n",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertTrue(
            any("missing Expected/expected" in p for p in problems), problems
        )
        # "unexpected" is not an expectation marker: it must still be a violation.
        card = replace(
            GOOD_CARD,
            "1. `grep -q '^\\[x\\]' todos.txt` -> Expected exit 0\n\n",
            "1. `grep -q '^\\[x\\]' todos.txt` -> unexpected output is a failure\n\n",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertTrue(
            any("criterion 1: missing Expected/expected" in p for p in problems),
            problems,
        )
        # ... nor is "expectedly": the marker must end as a word too.
        card = replace(
            GOOD_CARD,
            "1. `grep -q '^\\[x\\]' todos.txt` -> Expected exit 0\n\n",
            "1. `grep -q '^\\[x\\]' todos.txt` -> it expectedly fails\n\n",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertTrue(
            any("criterion 1: missing Expected/expected" in p for p in problems),
            problems,
        )
        # A Chinese card may write the marker as 期望.
        card = replace(
            GOOD_CARD,
            "1. `grep -q '^\\[x\\]' todos.txt` -> Expected exit 0\n\n",
            "1. `grep -q '^\\[x\\]' todos.txt` -> 期望退出码 0\n\n",
        )
        self.assertEqual((0, []), lint_text(card))

    def test_missing_risks(self):
        card = replace(
            GOOD_CARD,
            "- Tags may be misspelled -> criterion 1.\n",
            "\n",
        )
        code, problems = lint_text(card)
        self.assertEqual(1, code)
        self.assertIn("missing section: Risks", problems)

    def test_usage_exit2(self):
        result = subprocess.run(
            [sys.executable, "card_lint.py"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)

    def test_missing_file_exit2(self):
        result = subprocess.run(
            [sys.executable, "card_lint.py", os.path.join(ROOT, "no_such_card.md")],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(2, result.returncode)
        # A file that exists but is not UTF-8 is equally unreadable: still 2.
        with tempfile.TemporaryDirectory(prefix="card_lint_") as directory:
            undecodable = os.path.join(directory, "latin1.md")
            with open(undecodable, "wb") as handle:
                handle.write("## Goal\n\ncaf\xe9\n".encode("latin-1"))
            result = subprocess.run(
                [sys.executable, "card_lint.py", undecodable],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
        self.assertEqual(2, result.returncode)
        self.assertTrue(result.stderr.strip())


if __name__ == "__main__":
    unittest.main()
