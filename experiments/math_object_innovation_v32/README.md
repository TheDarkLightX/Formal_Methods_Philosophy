## v32, ordered refill basis compiler frontier

### Structural target

Search for an exact ordered compiler over the six essential refill basis bits from
`v31`.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v31`
- Same 3-state training set
- Same 13-state holdout set
- Same 130 residual-consistent viable behaviors

### Question

The `v31` result showed that the Horn-closed refill basis

- `B = {3,6,8,9,10,12}`

is irredundant.

This cycle asks whether there is a simpler ordered compiler law:

- choose an order `σ` on `B`
- read only the first `k` active basis bits in that order
- combine that truncated active-prefix with holdout score
- ask whether that already determines the first-refuter label

### Strongest claim

In the monotone refill transfer case, the essential six-bit basis admits an
ordered compiler law. No order is exact with only the first 3 active basis bits,
some orders are exact with the first 4 active basis bits, and every order is
exact with the first 5 active basis bits.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`

