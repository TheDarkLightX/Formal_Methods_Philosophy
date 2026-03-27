## v31, irredundant refill Horn basis frontier

### Structural target

Test whether the exact 6-bit Horn-closed semantic basis from `v29` and `v30` is
irredundant in the monotone refill transfer case.

### Bounded domain

- Same monotone refill-style controller family as `v29`
- Same 3-state training set
- Same 13-state holdout set
- Same 130 residual-consistent viable behaviors

### Question

The `v30` result showed:

- the 6-bit basis from `v29` stays minimal even after Horn closure
- its Horn closure reaches 11 of the 13 error bits
- the missing bits 5 and 11 are not derivable by the searched Horn library

This cycle asks two follow-up questions:

1. Is each of the 6 retained basis bits actually necessary for exact
   first-refuter classification?
2. Are the two missing bits operationally needed for exact classification, or are
   they only logically independent?

### Strongest claim

In the monotone refill transfer case, the Horn-closed 6-bit semantic basis is
irredundant: dropping any one of its six bits destroys exact first-refuter
classification. At the same time, the two non-derivable bits from `v30` are not
required for exact classification. Adding either one can split already-pure
buckets, but it does not improve label exactness.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
