# v18: safe-region certificate frontier

## Structural target

Search for the smallest conjunction of atomic winner-feature clauses that certifies a whole safe
region, not just the single winning repair program.

The bounded question is:

- inside the `7104` residual-consistent repair-program frontier,
- does there exist a tiny conjunction of winner-feature atoms such that:
  - every pair satisfying it is safe on the exhaustive reachable `4x4` verifier,
  - and the certified region contains more than one safe pair?

## Atom language

The atom language is inherited from `v17`:

- `holdout_total = value`
- `holdout_5_hits = value`
- `holdout_6_hits = value`
- `c1.feature = value`
- `c2.feature = value`

where the values come from the top ranked safe winner.

## Bounded domain

- the cached `7104` residual-consistent repair-program frontier from `v15`
- the cached `4263` unique verifier patterns from `v15`

## Allowed claim

If a conjunction is found such that every satisfying pair is safe, it is a sound region
certificate in this bounded model.
