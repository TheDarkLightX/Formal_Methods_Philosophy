# v79: hard decomposition-language boundary

## Structural target

Compare the hard witness-language frontier against a different family:
exact decomposition languages.

The concrete question is:

> on the exact hard merged-region partition from `v44`, does exact bit-fiber
> decomposition beat the current label-level witness languages?

## Bounded domain

- the hard refill witness frontier reused from `v44` and `v46`
- same exact merged-region partition:
  - `(7)`
  - `(8)`
  - `(9)`
  - `(10,11)`
  - `(12)`
- same `v38` feature surface
- same conjunction atom grammar of `1` to `4` signed literals

## Main bounded result

Exact bit-fiber decomposition exists, but it is strictly worse than the current
label-level witness languages.

Totals:

- exact bit-fiber decomposition:
  - total cost `24`
  - shared schema count `21`
- exact label-level witness language:
  - total cost `22`
  - shared schema count `19`

Per-region exact bit totals:

- `(7)`:
  - `4`
- `(8)`:
  - `5`
- `(9)`:
  - `7`
- `(10,11)`:
  - `6`
- `(12)`:
  - `2`

So the hardest losses are:

- `(10,11)`:
  - bit-fiber `6`
  - label-level `5`
- `(12)`:
  - bit-fiber `2`
  - label-level `1`

## Why it mattered

The next honest comparison after `v78` was not another witness-cover variant.
It was a different language family.

This cycle shows a clean boundary:

- decomposition is available
- but on this bounded frontier it is not the best exact language family

So minimal witness-language discovery does not automatically escalate toward
decomposition.

It still has to earn that move on the bounded corpus.

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the hard refill witness frontier, exact bit-fiber decomposition is strictly
worse than the current label-level witness language, both in local cost and in
shared schema count.

## Boundary learned

This compares one decomposition family against the current label-level witness
family.

The next honest step is:

- compare against certificate languages on the same hard frontier,
- or search for richer decomposition languages that are not limited to raw
  label bits
