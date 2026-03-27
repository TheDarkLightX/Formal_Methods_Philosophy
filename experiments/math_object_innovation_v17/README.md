# v17: winner-certificate language frontier

## Structural target

Search for a tiny sound certificate language that certifies the winning repair program selected by
the staged loop.

This is intentionally narrower than certifying the entire safe set.

The bounded question is:

- among the `7104` residual-consistent repair-program pairs,
- can a small conjunction of atomic winner-features isolate the safe winner exactly?

## Certificate model

Atomic certificate clauses are of the form:

- `holdout_total = value`
- `holdout_5_hits = value`
- `holdout_6_hits = value`
- `c1.feature = value`
- `c2.feature = value`

where `c1` and `c2` are the two repair clauses of the winning pair.

The loop searches for the smallest conjunction of such atoms that excludes every other
residual-consistent pair.

## Bounded domain

- the cached `7104` residual-consistent repair-program frontier from `v15`
- the safe winner from `v15`

## Allowed claim

If a minimal conjunction exists, it is a sound winner certificate in this bounded model because it
selects only the already certified safe winner.
