# v84: hard critical-region certificate widening boundary

## Question

On the hard refill witness frontier from `v83`, does widening strict
all-positive certificates from the `1..4` literal conjunction grammar to the
`1..5` literal conjunction grammar materially change the obstruction, or was the
old wall already stable on the critical regions that actually drive the optimal
partition-aware residual-budget ladder?

## Method

Scope the check to the exact union of score regions that appear in the optimal
`v83` partitions:

- `(7,12)`
- `(8)`
- `(9,10)`
- `(11)`
- `(9)`
- `(10,11)`
- `(7)`
- `(12)`

For each region:

- compute the exact all-positive certificate cover in the `1..4` literal
  signed-conjunction grammar,
- recompute in the widened `1..5` literal grammar,
- compare exact feasibility and minimal total certificate cost.

This is a bounded critical-region phase test. It does not claim that the full
joint `v83` search has already been re-solved in the widened grammar.

## Result

Only one critical region changes:

- `(10,11)`:
  - `1..4` literals: impossible
  - `1..5` literals: exact, total cost `6`

Every other critical region is unchanged:

- `(7,12)`: `7 -> 7`
- `(8)`: `7 -> 7`
- `(9,10)`: `10 -> 10`
- `(11)`: `6 -> 6`
- `(9)`: `9 -> 9`
- `(7)`: `5 -> 5`
- `(12)`: `2 -> 2`

The new exact all-positive cover for `(10,11)` in the widened grammar is:

- `(0, 0, 1, 1)`:
  - `err[3]`
- `(0, 1, 1, 0)`:
  - `err[6]`
- `(1, 0, 0, 1)`:
  - `err[8]`
- `(1, 0, 1, 0)`:
  - `err[9]`
- `(1, 0, 1, 1)`:
  - `not err[3] and not err[6] and not err[8] and not err[9] and err[10]`
- `(1, 1, 0, 0)`:
  - `not err[6] and not err[9] and not err[10]`

## Why it matters

`v80` and `v81` established a hard certificate obstruction at `(10,11)`, and
`v83` showed that score partition must join the residual-budget search.

`v84` sharpens the interpretation:

- the obstruction is not uniform across the critical hard regions,
- widening the certificate grammar does not help the other critical regions,
- the old wall was partly a grammar wall, localized at `(10,11)`.

So the current hard-frontier ceiling is likely close to the limit of the
`1..4` literal certificate grammar, but it is not yet the limit of exact
symbolic languages on this frontier.

## Status

Survivor. The bounded critical-region widening claim is exact.

## Next

- rerun the full joint partition-aware search in the widened grammar,
- or compare the widened certificate grammar against the current
  partition-aware residual-budget witness language on a second hard frontier.
