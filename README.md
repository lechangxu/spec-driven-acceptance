# spec-driven-acceptance
[![tests](https://github.com/lechangxu/spec-driven-acceptance/actions/workflows/tests.yml/badge.svg)](https://github.com/lechangxu/spec-driven-acceptance/actions/workflows/tests.yml)

**Write the spec first, then let a machine decide whether the work is done.**

([中文版本](README.zh-CN.md))

Most tasks handed to an AI coding agent fail in the same place: nobody agreed in advance what
"finished" would look like, so the agent reports success and a human re-reads the diff hoping to
spot trouble. This repository is the written half of a discipline that takes the decision out of
that hope.

## The problem

- "Done" is a claim made by the party that wants to be done.
- Review attention is scarce and unevenly spent; the tenth diff of the day gets a
  glance.
- Review quality is invisible: nobody records how often a review let a defect
  through, so a good reviewer is indistinguishable from a confident one.

## The method

What follows is what spec-driven development looks like when the spec is also the acceptance
contract — not a document written once and abandoned.

Six layers, cheapest first. Each layer states what it guarantees, what it cannot catch, and where a
failure should go back to.

1. **Spec** — the requirement written down as behaviour, not as intent.
2. **Task card** — the spec frozen into a document that also carries decisions,
   risks, acceptance criteria and boundaries.
3. **Machine criteria** — every acceptance line is a command with an expected
   result, so "done" is a return code, not a sentence.
4. **Deterministic scan** — linters and greps over the new lines only, for the
   failure shapes that are cheap to see mechanically.
5. **Independent review** — a reviewer that did not write the code, and was not
   told to be agreeable.
6. **Feedback measurement** — both kinds of mistake are counted, so the pipeline
   itself can be tuned.

The full walkthrough, with a data-flow diagram, is in
[docs/acceptance-pipeline.md](docs/acceptance-pipeline.md).

- [docs/judge-independence.md](docs/judge-independence.md) — why the session that
  wrote the code must never grade it.
- [docs/misjudgment-monitoring.md](docs/misjudgment-monitoring.md) — counting a
  review's errors in both directions, and why the numbers rot.

## Quick start

The card is the artefact. Try the linter on the worked example:

```bash
python3 card_lint.py examples/task-card.example.md
```

It prints `OK` and exits 0 when the card could be accepted mechanically. Break the card — delete a
section, drop a criterion's command — and it exits 1 naming the violation. A missing file or wrong
argument count exits 2: "could not check" must never be confused with "checked and fine".

Shape it enforces:

- the six sections `Goal`, `Decisions`, `Spec`, `Risks`, `Acceptance`, `Boundaries`;
- at least two acceptance criteria — a criterion is any list item under
  `Acceptance`, numbered or bulleted, so a bullet cannot carry an unprovable
  claim past the checks; subsections do not close the section, so a criterion
  added under a deeper heading is still checked;
- a backticked command and an `Expected` (or `期望`) note on every criterion —
  the word has to stand alone, so "unexpected output" does not count;
- at least one entry under `Risks`.

It deliberately does not judge whether the command proves the claim. That is a human decision, made
once, when the card is written.

Run the tests with:

```bash
python3 -m unittest discover -s tests -v
```

No dependencies beyond the standard library, Python 3.9+.

## Tech stack

| Layer | What it is |
| :--- | :--- |
| Language & runtime | Python 3.9+, standard library only — no third-party dependencies |
| Tests | unittest, 8 test cases: `python3 -m unittest discover -s tests -v` |
| CI | GitHub Actions, Python 3.12, workflow `.github/workflows/tests.yml` |

## Example output

The linter on the worked example — a card that passes:

```bash
python3 card_lint.py examples/task-card.example.md
```

```text
OK
```

`exit 0`

A broken card — reproduce it with a file whose whole content is `# demo`, a blank line, and `## Goal`:

```bash
printf '# demo\n\n## Goal\n' > /tmp/bad-card.md
python3 card_lint.py /tmp/bad-card.md
```

```
missing section: Decisions
missing section: Spec
missing section: Risks
missing section: Acceptance
missing section: Boundaries
Acceptance needs at least 2 criteria (found 0)
```

`exit 1`

No argument at all — "could not check", not "checked and fine":

```bash
python3 card_lint.py
```

```text
usage: card_lint.py <card.md>
```

`exit 2`

## What this is not

It is not a framework, a service, or a wrapper around a model. It is one document pattern and ninety
lines of Python that enforce its shape. The interesting part is the argument, not the code.

## Limitations

- Green only proves the criteria were met, and criteria can be weak.
- The linter checks form; a card can be well shaped and wrong.
- Everything here is tuned for small, reviewable diffs.

## License

MIT. See [LICENSE](LICENSE).
