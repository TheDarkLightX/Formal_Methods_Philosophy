## v37, refill concept-market frontier

### Structural target

Test whether a single invented pure concept can improve the exact explanatory
ladder on the hard monotone refill transfer frontier from `v34`.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v34`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same exact ordered basis from `v34`:
  - `(3, 6, 8, 9, 10, 12)`

### Searched concept grammars

1. Fixed-order insertion grammar
   - keep the exact `v34` order
   - add one invented primitive at one insertion position
   - primitive semantics:
     - `OR` of `2` or `3` basis bits, or
     - `AND` of `2` or `3` basis bits
   - re-optimize local ladder depths exactly

2. Replacement grammar
   - replace the source basis bits by one invented primitive
   - primitive semantics:
     - `OR` of `2` or `3` basis bits, or
     - `AND` of `2` or `3` basis bits
   - allow full reordering of the new feature language
   - ask whether any exact ladder survives at all

### Question

The `v36` primitive-invention result was easy-domain evidence on the repaired
verifier frontier.

This cycle asks whether simple pure concept invention still buys leverage on the
hard refill ladder frontier, and whether that leverage comes from:

- adding a shortcut concept on top of the basis, or
- replacing the basis by a smaller concept language.

### Strongest claim

In the hard monotone refill transfer case, simple pure concept invention is
real but fragile.

In the searched fixed-order insertion grammar, the best exact ladder inserts
`err[10] AND err[12]` before `err[10]`, lowering weighted cost from `118` to
`90` and reducing maximum depth from `4` to `3`.

In the searched replacement grammar, no single `2`- or `3`-bit pure `AND` or
`OR` primitive yields any exact ladder at all.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
