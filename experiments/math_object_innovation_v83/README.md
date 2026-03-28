# v83: hard partition-aware residual-budget frontier

## Structural target

Sharpen `v82` by dropping the fixed `v44` partition and searching over score
partition and residual structure jointly.

The concrete question is:

> on the hard refill witness frontier, is the fixed `v44` partition still
> globally optimal once residual-region budget and shared-schema cost are
> optimized together?

## Bounded domain

- the same hard `v38` feature frontier reused from `v44`, `v46`, `v80`, `v81`,
  and `v82`
- nontrivial scores:
  - `7`
  - `8`
  - `9`
  - `10`
  - `11`
  - `12`
- same conjunction grammar:
  - `1` to `4` signed literals
- search space:
  - all set partitions of the nontrivial scores
  - all exact placements of a fixed number of residual-default regions
  - optimize global shared-schema count, then exact total cost

## Main bounded result

The fixed `v44` partition is not globally optimal for residual budgets `1`
through `4`.

Best exact shared-schema ladder after joint partition search:

- budget `1`:
  - shared schemas `24`
  - total cost `28`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9,10)`
    - `(11)`
  - residual regions:
    - `(8)`
- budget `2`:
  - shared schemas `22`
  - total cost `26`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9,10)`
    - `(11)`
  - residual regions:
    - `(8)`
    - `(9,10)`
- budget `3`:
  - shared schemas `20`
  - total cost `24`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
  - residual regions:
    - `(8)`
    - `(9)`
    - `(10,11)`
- budget `4`:
  - shared schemas `19`
  - total cost `23`
  - partition:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
  - residual regions:
    - `(7,12)`
    - `(8)`
    - `(9)`
    - `(10,11)`
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

Compared with the fixed-partition `v82` ladder, shared-schema count improves by
exactly `1` for budgets `1` through `4`, at the same exact total cost.

## Why it mattered

`v82` found a real global residual-budget law, but it was still conditioned on
one fixed partition.

`v83` shows that this was not the full object. On the same bounded frontier:

- the low-budget optima merge scores before choosing residual regions
- the fixed `v44` partition only returns at full residual budget
- the loop should therefore search partition and residual structure together
  rather than treating partition as frozen

So the sharper object is a partition-aware residual-budget witness language.

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the hard refill witness frontier, the fixed `v44` partition from `v81` and
`v82` is not globally optimal once score partition and residual structure are
searched jointly. For residual budgets `1` through `4`, the best global
shared-schema counts become `24, 22, 20, 19`, each improving `v82` by one
schema at the same exact total cost.

## Boundary learned

This is still one bounded frontier and one grammar.

The next honest step is:

- test whether the same partition-aware residual-budget effect survives in a
  richer certificate grammar,
- or transfer the same joint search to a second hard frontier
