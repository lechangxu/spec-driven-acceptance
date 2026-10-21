# Monitoring how often the gate is wrong

A review that is trusted but never measured drifts. Count the two ways a gate can be wrong, pick
thresholds that mean something, and accept that any sample used to measure it goes stale.

## Two errors, not one

Every gate decision is a binary call against a truth that arrives later:

| | Later judged defective | Later judged fine |
|---|---|---|
| **Gate blocked** | correct block | **false fail** — wasted rework, eroded trust |
| **Gate passed** | **escaped defect** — the expensive one | correct pass |

- **escaped defect**: gate said clean, and a defect later surfaced in the same
  change. Cost: whatever the defect cost, times the share nobody caught next.
- **false fail**: an objection that did not survive scrutiny. Cost: rework time,
  plus the slow corrosion of people routing around the gate.

Measuring only one guarantees the other grows. A gate tuned purely to stop escapes converges on
blocking everything.

## How to sample

You cannot label every decision; label a sample, blind.

1. **Draw continuously, not conveniently.** Take the next N decisions as they occur.
   Reviewers who choose their own audit sample ask the easiest questions first.
2. **Keep the sample frame.** Record gate version, diff size, change kind. Rates on a
   mixed frame cannot tell a regression from a change in the mix.
3. **Label against outcomes, not opinions.** An escaped defect needs a later event:
   a revert, a bug report, a downstream failure traced to the change.
4. **Quote findings verbatim.** Paraphrasing during labelling turns a real block into
   a remembered false fail.
5. **Stratify by severity.** One escaped data-loss defect outweighs twenty typos.

## Choosing thresholds

A threshold needs a denominator and a direction, or it is decoration:

- state rates over a window: escaped defects per 100 passed changes, false fails per
  100 blocks;
- set the threshold from observed history plus an allowance, not from ambition — a
  gate that starts at "zero escapes" is turned off within a month;
- track both rates together. Escapes falling while false fails triple means the gate
  got stricter, not better, and the two eras are not comparable;
- re-derive after any change to criteria, reviewer, or sample frame. Mixing eras is
  the most common way these numbers become unreadable.

## Samples rot

The corpus you calibrated on describes one quarter's work: those change types, those reviewers, that
codebase. Six months on, the same document is still quoted and the numbers no longer describe
anything.

- **Resample on a schedule**, and record the draw date next to every rate.
- **Record the sampling frame** with the number, not just the number.
- **Retire entries whose trigger condition is gone.** A stale threshold is more
  dangerous than a missing one: it turns "never measured" into "measured once, fine".
- **Re-open a verdict when the premise changes.** A rejection argued from a
  repository state that has since been rebuilt is not evidence about the new state.

## The meta-rule

The gate is a measuring instrument. Instruments get calibrated, and calibrations get dated. A rate
whose sample origin is not written beside it is an opinion.
