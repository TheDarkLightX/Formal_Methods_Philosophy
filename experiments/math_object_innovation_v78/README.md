# v78: hard witness-language phase diagram

## Structural target

Repeat the `v77` phase-diagram idea on a harder bounded frontier where the exact
families should separate instead of tying.

## Bounded domain

- the hard refill witness frontier built in `v40`, `v44`, and `v46`
- same monotone refill-style controller family as `v29` to `v46`
- same `3` training states
- same `13` holdout states
- same `130` residual-consistent viable behaviors
- same `v38` feature surface

## Compared exact language families

1. score-local residual-default witness languages from `v40`
2. merged-region residual-default witness languages from `v44`
3. shared global witness-schema language from `v46`

## Main bounded result

This harder frontier does not produce a tie.

It gives a strict exact ladder:

- score-local residual-default witnesses:
  - cost `27`
- merged-region residual-default witnesses:
  - cost `22`
- shared global witness-schema language:
  - size `19`

The exact merged-region partition remains:

- `(7)`
- `(8)`
- `(9)`
- `(10,11)`
- `(12)`

And the local all-positive witness family already fails on:

- `9`
- `10`

## Why it mattered

`v77` showed that one repaired verifier frontier had multiple tied optima once
the witness contract was fixed.

`v78` shows a harder case where widening the witness contract gives a strict
ordering instead:

- local exact witnesses
- then merged-region witnesses
- then shared global schemas

So minimal witness-language discovery is not only a tie-breaking lens.

On this harder frontier, it orders the exact families.

## Claim tier

- tier:
  - `descriptive_oracle`
- oracle dependent:
  - yes

## Strongest claim

On the hard refill witness frontier, minimal witness-language discovery yields a
strict bounded ladder once the witness contract is widened. The harder frontier
therefore supports the same umbrella as `v77`, but in a stronger form.

## Boundary learned

This cycle still compares previously surviving exact families rather than
searching over a larger witness-language grammar directly.

The next honest step is:

- direct search over a wider bounded witness-language family on the same hard
  frontier,
- or a comparison against certificate or decomposition languages rather than
  only witness-cover languages
