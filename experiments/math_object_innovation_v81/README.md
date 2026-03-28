# v81: hard local residual-budget ladder

## Structural target

Compare strict all-positive certificates against a bounded amount of local
residual-default structure on the same hard merged-region partition.

The concrete question is:

> on the exact hard partition from `v44`, how many regions must be allowed
> residual-default witnessing before the searched language becomes exact again?

## Bounded domain

- the hard merged-region witness frontier reused from `v44` and `v80`
- same exact partition:
  - `(7)`
  - `(8)`
  - `(9)`
  - `(10,11)`
  - `(12)`
- same conjunction grammar:
  - `1` to `4` signed literals over the `v38` feature surface
- region language options:
  - residual-default witness region, as in `v44`
  - all-positive certificate region, as in `v80`

## Main bounded result

Strict all-positive certification is impossible on this partition, but exactness
returns as soon as one region is allowed residual-default witnessing.

That minimal exact region is forced:

- `(10,11)`

Best exact total cost by residual-region budget:

- `0` residual regions:
  - impossible
- `1` residual region:
  - cost `28`
  - shared schemas `26`
  - best subset:
    - `(10,11)`
- `2` residual regions:
  - cost `26`
  - shared schemas `24`
  - best subsets:
    - `(8), (10,11)`
    - `(9), (10,11)`
- `3` residual regions:
  - cost `24`
  - shared schemas `22`
  - best subset:
    - `(8), (9), (10,11)`
- `4` residual regions:
  - cost `23`
  - shared schemas `21`
  - best subsets:
    - `(7), (8), (9), (10,11)`
    - `(8), (9), (10,11), (12)`
- `5` residual regions:
  - cost `22`
  - shared schemas `20`
  - all regions

## Why it mattered

`v80` showed that strict all-positive certificates already fail on `(10,11)`.

`v81` sharpens that boundary:

- residual structure is not all-or-nothing
- one local residual region is already sufficient for exactness
- but that first residual region is forced
- once exactness is restored, more residual freedom yields a strict bounded cost
  ladder

So on this frontier the right object is not only "certificate or witness."
It is a residual-budgeted witness language.

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the hard merged-region witness frontier, exactness in the searched
`1`-to-`4`-literal conjunction grammar already returns once a single region is
allowed residual-default witnessing, but that region is forced to be `(10,11)`.
As the residual budget rises from `1` to `5` regions, the best exact total cost
drops strictly from `28` to `26` to `24` to `23` to `22`.

## Boundary learned

This is still a local residual-budget search on one fixed hard partition.

The next honest step is:

- search richer certificate languages with local residual structure on the same
  hard frontier,
- or compare this residual-budget ladder against a more global shared-schema
  optimization
