## v38, refill two-concept ladder frontier

### Structural target

Test whether two invented pure shortcut concepts can improve the exact hard
refill ladder from `v37`.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v37`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same exact base order from `v34`:
  - `(3, 6, 8, 9, 10, 12)`

### Searched grammar

- keep the exact base order
- insert two distinct pure primitives
- primitive semantics:
  - `OR` of `2` or `3` basis bits, or
  - `AND` of `2` or `3` basis bits
- allow arbitrary insertion positions for both primitives
- re-optimize local ladder depths exactly

### Question

`v37` showed that one inserted shortcut concept can lower weighted cost from
`118` to `90`, but also that one searched replacement concept cannot collapse
the hard basis.

This cycle asks whether a second inserted shortcut can materially lower the hard
ladder again.

### Strongest claim

In the hard monotone refill transfer case, two inserted pure shortcut concepts
improve the exact ladder again.

In the searched grammar, the best exact pair is:

- `err[6] AND err[10] AND err[12]`
- `err[9] AND err[10] AND err[12]`

with order:

- `err[6] AND err[10] AND err[12]`
- `err[3]`
- `err[9] AND err[10] AND err[12]`
- `err[6]`
- `err[8]`
- `err[9]`
- `err[10]`
- `err[12]`

This yields:

- weighted cost `80`
- maximum depth `2`

No exact pair in the searched grammar reaches maximum depth `1`.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
