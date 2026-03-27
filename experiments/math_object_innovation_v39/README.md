## v39, anchored third-shortcut boundary frontier

### Structural target

Test whether a third pure shortcut concept can improve the exact hard refill
ladder once the best exact two-shortcut pair from `v38` is fixed.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v38`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Fixed exact pair from `v38`:
  - `err[6] AND err[10] AND err[12]`
  - `err[9] AND err[10] AND err[12]`
- Fixed base order from `v38`:
  - `err[6] AND err[10] AND err[12]`
  - `err[3]`
  - `err[9] AND err[10] AND err[12]`
  - `err[6]`
  - `err[8]`
  - `err[9]`
  - `err[10]`
  - `err[12]`

### Searched grammar

- keep the exact `v38` pair fixed
- insert one additional pure primitive
- primitive semantics:
  - `OR` of `2` or `3` basis bits, or
  - `AND` of `2` or `3` basis bits
- allow arbitrary insertion position
- re-optimize local ladder depths exactly

### Question

`v38` showed that two shortcut concepts can lower the hard refill ladder to
weighted cost `80` and max depth `2`.

This cycle asks whether that exact pair is locally saturated under one more
simple pure shortcut.

### Strongest claim

In the anchored third-shortcut grammar, no searched third shortcut lowers the
exact hard refill ladder below weighted cost `80` or max depth `2`.

The best searched extra shortcut is:

- `err[3] OR err[6] OR err[8]`

inserted after `err[9]`, which preserves:

- weighted cost `80`
- max depth `2`

but improves bucket count from `51` to `48`.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
