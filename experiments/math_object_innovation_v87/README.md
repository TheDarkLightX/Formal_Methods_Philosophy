# v87: low-residual widened-certificate saturation boundary

## Question

`v86` closed the high-residual end of the widened-certificate axis:

- widening strict certificates from the `1..5` literal grammar to the `1..6`
  literal grammar did not move budgets `3`, `4`, or `5`

That left one exact open slice:

> if strict certificates widen from `1..5` literals to `1..6` literals, do
> budgets `0`, `1`, or `2` move beyond the `v85` frontier?

## Method

Reuse the exact hard frontier from `v85`:

- search all score partitions of:
  - `7, 8, 9, 10, 11, 12`
- optimize:
  - global shared-schema count
  - then exact total cost

Language split:

- residual-default witness regions stay in the `1..4` literal grammar
- strict certificate regions widen from the `1..5` grammar in `v85` to the
  `1..6` grammar here

Scope only the low-residual slice:

- budget `0`
- budget `1`
- budget `2`

## Main bounded result

Nothing moves.

Exact widened low-residual ladder:

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

Compared with `v85`:

- schema gain:
  - `0, 0, 0`
- cost gain:
  - `0, 0, 0`

## Why it matters

`v85` showed that widening strict certificates from `1..4` to `1..5` literals
helped only the low-residual regime.

`v86` showed that the high-residual regime does not move under another width
increase.

`v87` closes the remaining gap:

- budgets `0`, `1`, and `2` also do not move when strict certificates widen
  from `1..5` to `1..6` literals
- so the full hard partition-aware residual-budget ladder is now locally
  saturated along this literal-width axis

This does not prove that no richer certificate language can help. It shows only
that one more conjunction-width increase does not help any residual budget on
this bounded frontier.

## Status

Survivor. The low-residual saturation claim is exact on the same bounded hard
frontier.

## Next

- transfer the widened-certificate search to a second hard frontier
- or switch from wider conjunctions to a genuinely richer certificate language
