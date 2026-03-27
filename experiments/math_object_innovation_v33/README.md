## v33, k4 refill order law frontier

### Structural target

Find an exact criterion for which 4-prefix orders are exact in the monotone refill
ordered-basis compiler frontier from `v32`.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v32`
- Same 3-state training set
- Same 13-state holdout set
- Same 130 residual-consistent viable behaviors
- Same essential refill basis `B = {3,6,8,9,10,12}`

### Question

`v32` showed:

- no order is exact for `k=3`
- some orders are exact for `k=4`
- every order is exact for `k=5`

This cycle asks for an exact characterization of the `k=4` exact orders.

### Strongest claim

Let `σ` be an order on `B`, and let `F4(σ)` be its first four positions.
Then `Exact_4(σ)` holds if and only if:

1. `3 ∈ F4(σ)` and `F4(σ)` contains at least one of `{6,8}`, or
2. `3 ∉ F4(σ)`, both `6` and `8` lie in `F4(σ)`, and `3` appears before the
   unique omitted bit from `{9,10,12}`.

This criterion matches all `720` orders exactly.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`

