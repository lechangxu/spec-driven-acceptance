# Judge independence

The rule: **the context that wrote the code does not get to review it.** Not because the writer is
dishonest, but because the writer already believes a story about the change, and re-reading the diff
confirms the story.

## Why an LLM judge must not grade its own work

Four mechanisms, each enough on its own:

1. **Framing.** The author knows what the code was meant to do and reads it as doing
   that. A reviewer with no memory of the intent reads what is on the page.
2. **Sunk cost.** Effort spent makes a defect feel like something to fix later.
3. **Effort asymmetry.** Re-reading carefully is slower than asserting confidently.
4. **Continuity bias.** A critic asked to finish the job tends to help finish it.
   Sympathy is a virtue in a colleague and a bug in a gate.

Telling the author to be rigorous fixes none of these. Rigour is not the bottleneck; the standpoint
is.

## What makes a reviewer independent

Independence is a property of the setup, not an intention:

- **Separate context.** A fresh session that never saw the implementation
  conversation — not a fresh prompt in the same one. Carry the diff and the card.
- **Different lineage.** Same-family writers and reviewers share blind spots and
  enthusiasms. Heterogeneity does not guarantee quality; it decorrelates failures.
- **Not asked to be helpful.** Ask for defects and citation, and say plainly that
  "no findings" is allowed. "Be constructive" reads as "find something to praise".
- **A diff, not a summary.** Summaries inherit the author's framing.
- **Blind to the verdict you want.** A reviewer that can see "tests are green, ship
  it" will find a way to agree.

## Majority, and what a single no means

- verdicts collected independently, then compared;
- a **block** needs the majority, not a single dissenter;
- a single dissent is a **concern**: recorded, addressed or explicitly dismissed,
  never silently dropped.

The asymmetry is deliberate. One reviewer able to veto anything will eventually veto everything and
lock the pipeline solid; one whose objection is recorded still puts the question in front of the
author, which is most of the value. Headcount matters less than calibration — see [misjudgment-
monitoring.md](misjudgment-monitoring.md).

## The escape hatch, and its cost

There is always a reason to skip review. Write the exception down when you take it and mark the
verdict self-reviewed. The cost is not that the exception is wrong; it is that an undocumented
exception is indistinguishable from a gate that never existed.

## Checklist

- [ ] Review ran in a context that did not write the code.
- [ ] It received the diff and the card, not a summary or test output.
- [ ] The prompt allowed "no findings" and forbade praise.
- [ ] Verdicts were collected before comparison.
- [ ] A single no produced a recorded concern; skipped reviews are logged.
