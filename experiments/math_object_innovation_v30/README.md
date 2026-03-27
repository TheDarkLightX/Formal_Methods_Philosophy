# v30: horn-closed refill basis frontier

## Structural target

Test whether the 6-bit exact semantic basis from `v29` can shrink once error-bit implications are
allowed.

The bounded question is:

- in the monotone refill transfer case,
- compute the exact single- and pair-Horn implications among the 13 holdout error bits,
- then ask whether `holdout score + closure(B)` can recover the first-refuter partition with a basis
  smaller than the 6-bit basis from `v29`.

## Bounded domain

- the same `130` viable behaviors from `v29`
- `13` holdout error bits
- exact Horn implication language:
  - antecedent size `1`
  - antecedent size `2`
  - single consequent bit

## Allowed claim

If Horn closure from the 6-bit basis derives many additional error bits but no smaller basis works,
then the `v29` basis is robust under the searched implication closure, not just a raw feature list.
