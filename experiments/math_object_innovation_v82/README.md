# v82: hard residual-budget schema ladder

## Structural target

Sharpen `v81` by switching from local witness-cost accounting to global
shared-schema accounting on the same hard merged-region partition.

The concrete question is:

> if a fixed number of regions may use residual-default witnessing, how much
> further can exact description size fall once schema sharing is optimized
> globally across all regions?

## Bounded domain

- the hard merged-region witness frontier reused from `v44`, `v46`, `v80`, and
  `v81`
- same exact partition:
  - `(7)`
  - `(8)`
  - `(9)`
  - `(10,11)`
  - `(12)`
- same conjunction grammar:
  - `1` to `4` signed literals over the `v38` feature surface
- same region language options:
  - residual-default witness region
  - all-positive certificate region
- new objective:
  - minimize distinct shared schemas globally for each fixed residual budget

## Main bounded result

Global schema sharing strictly sharpens the local `v81` ladder at every
feasible residual budget.

Exact shared-schema ladder:

- `0` residual regions:
  - impossible
- `1` residual region:
  - shared schemas `25`
  - total cost `28`
  - best subset:
    - `(10,11)`
- `2` residual regions:
  - shared schemas `23`
  - total cost `26`
  - best subset:
    - `(8), (10,11)`
- `3` residual regions:
  - shared schemas `21`
  - total cost `24`
  - best subset:
    - `(8), (9), (10,11)`
- `4` residual regions:
  - shared schemas `20`
  - total cost `23`
  - best subset:
    - `(7), (8), (9), (10,11)`
- `5` residual regions:
  - shared schemas `19`
  - total cost `22`
  - all regions

Compared with `v81`, the global shared-schema count drops by exactly `1` at
every feasible residual budget:

- `26 -> 25`
- `24 -> 23`
- `22 -> 21`
- `21 -> 20`
- `20 -> 19`

The full-budget endpoint recovers the exact shared-schema optimum from `v46`.

## Why it mattered

`v81` showed that local residual structure is budgetable.

`v82` shows that this was still not the end of the line. On the same hard
partition:

- the residual-budget ladder survives under a more global objective
- global schema sharing compresses every feasible rung
- and the full residual budget lands exactly on the earlier global optimum

So the sharper object is not only a residual-budgeted witness language. It is a
residual-budgeted witness language with a global schema-sharing law.

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the hard merged-region witness frontier, global schema sharing strictly
sharpens the local residual-budget ladder from `v81`. At every feasible
residual budget from `1` through `5` regions, the best exact shared-schema
count drops by `1` relative to the local count, yielding the exact ladder
`25, 23, 21, 20, 19` while preserving the same total-cost ladder
`28, 26, 24, 23, 22`.

## Boundary learned

This is still a fixed-partition result on one hard frontier.

The next honest step is:

- search richer certificate grammars with local residual structure on the same
  hard frontier,
- or ask whether a comparable global residual-budget law survives on a second
  hard frontier
