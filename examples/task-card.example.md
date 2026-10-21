# Task card: tag filtering for the `todo` command-line tool

> Fictional example. `todo` is a made-up project; every name here is invented.
> The point of the card is its shape, not the feature.

## Goal

Let `todo list` show only the items carrying a given tag, so a user with fifty
open items can read the three that matter right now.

## Decisions

1. Filtering happens at read time; the storage format does not change.
2. No tag means "no filter" — existing output stays byte-identical.
3. Unknown tags print an empty list and exit 0, not an error.

## Spec

- `todo list --tag <tag>` prints only items whose `#tag` matches exactly.
- `todo list --tag <tag> --json` emits the same filtered set as JSON.
- Matching is case-sensitive, and a tag is the token after `#` up to whitespace.

## Risks

1. **Existing output regresses when no tag is given** — whoever reads `--help`
   will not notice a stray blank line. Backstop: criterion 2 compares the
   unfiltered output against a stored golden file.
2. **`--json` path drifts from the plain path** — two code paths, one filter.
   Backstop: criterion 3 asserts the JSON item count equals the plain-line count.

## Acceptance

1. `python3 -m pytest tests/test_list.py -q` -> Expected exit 0, all tests pass
2. `todo list > /tmp/now.txt && diff -u tests/golden_list.txt /tmp/now.txt` -> Expected no diff
3. `todo list --tag work --json > /tmp/j.json && python3 -c "import json,sys; sys.exit(len(json.load(open('/tmp/j.json'))) != 2)"` -> Expected exit 0
4. `todo list --tag nosuchtag > /tmp/empty.txt; test $? -eq 0 && test ! -s /tmp/empty.txt` -> Expected exit 0

## Boundaries

- Do not change the on-disk format, add dependencies, or rename existing flags.
