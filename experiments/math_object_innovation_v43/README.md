## v43, unconstrained score-abstraction boundary frontier

### Structural target

Test whether the contiguous score-abstraction result from `v42` was only an
artifact of the contiguity restriction.

### Bounded domain

- Same monotone refill-style controller family as `v29` to `v42`
- Same 3-state training set
- Same 13-state holdout set
- Same `130` residual-consistent viable behaviors
- Same `v38` feature language with `8` features
- Same witness-atom grammar as `v40` to `v42`:
  - conjunctions of `1` to `3` signed literals
- Nontrivial scores:
  - `7, 8, 9, 10, 11, 12`

### Search space

- all set partitions of the six nontrivial scores
- exact positive-cover plus residual-default witness search inside each score
  region

### Question

`v42` found the best exact contiguous partition:

- `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`

with total witness cost `23`.

This cycle asks whether a non-contiguous score abstraction can do better.

### Strongest claim

In the searched unconstrained score-partition space:

- all `203` set partitions were checked
- only `10` were exact in the searched witness grammar
- the same partition from `v42` remains optimal:
  - `(7)`, `(8)`, `(9)`, `(10,11)`, `(12)`
- best total witness cost remains `23`

So contiguity was not the binding restriction in `v42`.

### Claim tier

- `tier = descriptive_oracle`
- `oracle_dependent = true`
