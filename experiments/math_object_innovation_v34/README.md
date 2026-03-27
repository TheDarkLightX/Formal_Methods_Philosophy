## v34, regional refill ladder frontier

### Structural target

Test whether the monotone refill transfer frontier admits a nonuniform
explanatory ladder, instead of one global explanation depth for every score
region.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v33`
- Same 3-state training set
- Same 13-state holdout set
- Same 130 residual-consistent viable behaviors
- Same essential basis `B = {3,6,8,9,10,12}`

### Question

The previous cycles found:

- a 6-bit irredundant basis
- an ordered compiler law
- and an exact structural criterion for the `k=4` exact orders

Those were still global statements.

This cycle asks whether different holdout-score regions can use different prefix
depths under one shared order.

### Ladder model

For an order `σ` on `B`, and each holdout score `s`, choose a local depth
`d_s ∈ {0,1,2,3,4,5}`.

The key for a candidate `x` is:

- `(S(x), Prefix_{d_{S(x)}}^σ(x))`

where `S(x)` is holdout score and `Prefix_k^σ(x)` is the first `k` active basis
bits in order `σ`.

The plan is exact if that key determines the first-refuter label.

### Strongest claim

In the monotone refill transfer case, the best exact regional ladder uses the
order `(3,6,8,9,10,12)` and local depths:

- `d_7 = 2`
- `d_8 = 3`
- `d_9 = 4`
- `d_10 = d_11 = d_12 = 1`
- all other score regions use `0`

This yields:

- weighted online cost `118`
- average depth `118 / 130`
- maximum depth `4`

For comparison:

- a global exact `k=4` compiler costs `520`
- a global `k=5` compiler costs `650`

Also, no exact regional ladder exists with maximum depth `3`.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`

