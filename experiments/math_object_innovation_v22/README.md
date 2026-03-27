# v22: arithmetic refuter logic frontier

## Structural target

Compress the scalar refuter quotient into a tiny exact arithmetic logic.

The bounded question is:

- inside the `7104`-pair residual-consistent repair-program frontier,
- can the four first-refuter labels be classified exactly by a short decision list over one scalar score coordinate,
- and if so, what is the smallest surviving arithmetic presentation?

## Bounded domain

- the cached `7104` residual-consistent repair-program frontier from `v15`
- the four `v21` refuter labels:
  - `safe`
  - `fail_13116`
  - `fail_1915`
  - `fail_828`
- scalar coordinates:
  - `holdout_total`
  - `holdout_5_hits`
  - `holdout_6_hits`
- atom grammar for scalar decision lists:
  - threshold atoms, `s > c`
  - equality atoms, `s = c`
  - congruence atoms, `s mod m = r`, with `2 <= m <= 30`

## Allowed claim

If a scalar coordinate admits an exact length-`3` decision list in this grammar, and no shorter list
exists, that is a real compression of the full refuter partition in this bounded model.

If a scalar coordinate contains a mixed bucket, then no scalar-only classifier over that coordinate
can be exact.
