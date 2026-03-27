## v45, five-literal witness-grammar boundary frontier

### Structural target

Test whether the live witness-grammar axis from `v44` still improves when the
atom grammar grows one step further, or whether the best exact hard-frontier
witness object is already stable.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v44`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same `v38` feature language with `8` features
- Same nontrivial scores:
  - `7, 8, 9, 10, 11, 12`
- Same unconstrained search over all `203` set partitions
- Compare two exact witness grammars:
  - conjunctions of `1` to `4` signed literals
  - conjunctions of `1` to `5` signed literals

### Question

`v44` showed that the witness grammar was still live even after the
score-partition axis saturated:

- best partition stayed `(7), (8), (9), (10,11), (12)`
- best total witness cost dropped from `23` to `22`

This cycle asks whether one more literal changes the best exact object again.

### Strongest claim

In the searched `1..5`-literal witness grammar:

- the feasible partition set stays the same as in `v44`
- the best partition stays the same:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- the best total positive-cover-plus-residual witness cost stays the same:
  - `22`

So `v44` improved the live grammar axis, but the next step does not improve the
main exact object.

There are still secondary changes:

- two non-best partitions improve by one unit each

but the main frontier is stable.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
