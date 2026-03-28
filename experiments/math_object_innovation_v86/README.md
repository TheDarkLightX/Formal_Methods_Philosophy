# v86: high-residual widened-certificate saturation boundary

## Question

`v85` showed that widening strict certificates from the `1..4` literal grammar
to the `1..5` literal grammar changes the full hard partition-aware frontier,
but only for low residual budgets:

- a new zero-residual exact rung appears
- budgets `1` and `2` improve
- budgets `3`, `4`, and `5` do not move

The next question is whether the high-residual end is still grammar-limited.

> if strict certificates widen again, from `1..5` literals to `1..6` literals,
> do budgets `3`, `4`, or `5` move?

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

Scope only the high-residual slice:

- budget `3`
- budget `4`
- budget `5`

## Main bounded result

Nothing moves.

Exact widened high-residual ladder:

- budget `3`:
  - shared schemas `20`
  - total cost `24`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
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

Compared with `v85`:

- schema gain:
  - `0, 0, 0`
- cost gain:
  - `0, 0, 0`

## Why it matters

`v85` established that the old hard ceiling was partly grammatical.

`v86` sharpens that claim:

- the remaining high-residual end does not move under another literal-width
  increase
- so the low-residual regime was grammar-blocked
- the high-residual regime is now locally saturated with respect to this
  widening axis

This does not prove that no richer certificate language can help. It only shows
that increasing conjunction width from `1..5` to `1..6` literals does not help
the high-residual end.

## Status

Survivor. The high-residual saturation claim is exact on the same bounded hard
frontier.

## Next

- transfer the widened-certificate search to a second hard frontier
- or switch from wider conjunctions to a genuinely richer certificate language
