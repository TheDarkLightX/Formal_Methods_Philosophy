# v23: mixed-bucket repair frontier

## Structural target

Repair the only scalar obstruction left after `v22`.

The bounded question is:

- `holdout_6_hits` fails scalar exactness only because the bucket `859` is mixed,
- does one tiny second coordinate repair that bucket exactly,
- and if so, what is the smallest surviving repair feature in a simple clause-feature library?

## Bounded domain

- the cached `7104` residual-consistent repair-program frontier from `v15`
- the four `v21` refuter labels
- primary scalar coordinate:
  - `holdout_6_hits`
- simple repair-feature library:
  - each component of `params_1`
  - each component of `params_2`
  - numeric slot equalities `params_1[i] = params_2[i]`, for `0 <= i < 5`
  - numeric slot comparisons `params_1[i] < params_2[i]`, for `0 <= i < 5`
  - string slot equalities for indices `5` and `6`

## Allowed claim

If exactly one simple repair feature makes `(holdout_6_hits, feature)` an exact quotient for the full
refuter partition, that is a real bounded repair law, not just a workaround.
