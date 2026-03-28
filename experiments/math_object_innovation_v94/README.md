# v94: dependency-aware obligation-fibered repair

## Question

The strongest recent meta-result, `v92`, was that the frontier moved when the
object of search changed, not when the old grammar was merely widened.

For software engineering, one natural next object is:

- failure obligations grouped into repair fibers

The bounded first question is:

> when a bug corpus decomposes into edit-site fibers, does fibered repair beat
> monolithic patch search, and what is the first exact correction once those
> fibers start to overlap?

## Method

Bounded domain:

- two tiny patch corpora, each with `27` patches
- three edit sites:
  - `guard`
  - `bounds`
  - `transform`
- patch family:
  - `3` choices per site
  - total:
    - `3^3 = 27`
- three unit-test fibers:
  - `guard` test
  - `bounds` test
  - `transform` test

Two corpora were searched:

1. `separable_patch_family`
   - the `bounds` test neutralizes `transform`
   - the three fibers are genuinely independent
2. `overlap_patch_family`
   - the `bounds` test overlaps with `transform`
   - naive independent fibering is no longer exact

Three loop styles were compared:

1. monolithic patch search over all `27` patches
2. naive obligation-fibered repair
3. dependency-aware obligation-fibered repair

The dependency-aware loop solves:

- `transform` first
- then solves `guard` and `bounds` conditioned on the discovered transform

## Main bounded result

The software-shaped survivor is:

- dependency-aware obligation-fibered repair

### Separable family

Monolithic patch search:

- average candidate-test evaluations:
  - `39.0`
- worst-case:
  - `39`

Naive fibered repair:

- average local evaluations:
  - `15.0`
- exact gold recovery:
  - `27 / 27`

Dependency-aware fibered repair:

- average local evaluations:
  - `9.0`
- exact gold recovery:
  - `27 / 27`

So on the exact separable family, fibered repair compresses the search from a
monolithic `39` evaluations to `9`.

### Overlap family

Monolithic patch search:

- average candidate-test evaluations:
  - `35.851851851851855`
- worst-case:
  - `39`

Naive fibered repair:

- average local evaluations:
  - `15.0`
- exact gold recovery:
  - `16 / 27`

Dependency-aware fibered repair:

- average local evaluations:
  - `9.0`
- exact gold recovery:
  - `27 / 27`

So the first overlap boundary is now explicit:

- plain independent fibering fails
- adding one dependency edge restores exactness

## Why it matters

This is the first bounded software-engineering-shaped survivor in the current
main line.

The important object is not just:

- a verifier classifier

It is:

- a dependency graph over repair fibers

That is a deeper loop family for software engineering:

1. carve failing obligations into fibers
2. solve the easiest independent fibers first
3. condition downstream fibers on those solved choices
4. compose the resulting repair

This is exactly the kind of search-object shift that has driven the strongest
progress elsewhere in the repo.

## Status

Survivor.

The bounded result does not claim this loop is universally best.
It does show:

- independent fibering already beats monolithic patch search on the separable
  corpus
- dependency-aware fibering is the first exact correction when fibers overlap

## Next

- test certificate-carrying repair on the same bounded bug corpus
- or search the smallest exact repair-language grammar after the dependency
  graph stabilizes
