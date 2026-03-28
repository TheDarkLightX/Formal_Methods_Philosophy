# v85: hard widened-certificate partition-aware residual-budget frontier

## Question

`v84` showed that, on the exact critical-region union induced by the `v83`
optima, widening strict all-positive certificates from the `1..4` literal
grammar to the `1..5` literal grammar changes only region `(10,11)`.

The next question is global:

> does that localized certificate widening actually change the full
> partition-aware residual-budget frontier, or does the old `v83` ladder remain
> unchanged after the joint search is rerun?

## Method

Repeat the full `v83` joint search:

- search all set partitions of nontrivial scores:
  - `7, 8, 9, 10, 11, 12`
- search all exact residual-region budgets
- optimize:
  - global shared-schema count
  - then exact total cost

Language split:

- residual-default witness regions stay in the `1..4` literal signed-conjunction
  grammar
- strict certificate regions widen to the `1..5` literal grammar

## Main bounded result

The localized `v84` change does propagate to the full joint frontier, but only
at low residual budgets.

Exact widened ladder:

- budget `0`:
  - shared schemas `25`
  - total cost `29`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
  - residual regions:
    - none
- budget `1`:
  - shared schemas `23`
  - total cost `27`
  - same partition
  - residual regions:
    - `(8)`
- budget `2`:
  - shared schemas `21`
  - total cost `25`
  - same partition
  - residual regions:
    - `(8)`
    - `(9)`
- budget `3`:
  - shared schemas `20`
  - total cost `24`
  - same partition
  - residual regions:
    - `(7,12)`
    - `(8)`
    - `(9)`
- budget `4`:
  - shared schemas `19`
  - total cost `23`
  - same partition
  - residual regions:
    - all four regions
- budget `5`:
  - shared schemas `19`
  - total cost `22`
  - partition:
    - `(7)`
    - `(8)`
    - `(9)`
    - `(10,11)`
    - `(12)`
  - residual regions:
    - all regions

Compared with `v83`:

- a new zero-residual all-positive rung now exists
- budget `1` improves:
  - `24, 28 -> 23, 27`
- budget `2` improves:
  - `22, 26 -> 21, 25`
- budgets `3`, `4`, and `5` are unchanged

## Why it matters

`v84` could still have been a local boundary with no global consequence.

`v85` shows that this is not what happened.

The widened certificate grammar changes the actual hard-frontier joint search,
but only in the low-residual regime.

So the sharper law is:

- the hard ceiling was partly grammatical
- widening certificates opens a new exact all-positive rung
- but once residual budget is large enough, the old `v83` frontier already had
  the right object

## Status

Survivor. The widened-certificate partition-aware residual-budget ladder is
exact on the same bounded hard frontier.

## Next

- transfer the same widened-certificate joint search to a second hard frontier
- or search whether a richer certificate grammar moves budgets `3` and above,
  where the `1..5` widening no longer helps
